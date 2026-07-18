from fastapi import FastAPI,Request , Depends , Response
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .routers import auth
from .models import RequestLog, Service, User, RequestLog
from .database import engine, Base, sessionLocal, get_db, wait_for_db
from .routers import analytics, proxy, admin
from .dependencies import get_session_user, get_current_user
from sqlalchemy.orm import Session 
from contextlib import asynccontextmanager
from .utils import monitor_services
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import iterate_in_threadpool
import time
import asyncio

wait_for_db()
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(repeat_health_check())
    yield
app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],expose_headers=["*"])
async def repeat_health_check():
    while True:
        db = sessionLocal()
        try:
            await monitor_services(db)
        except Exception as e:
            print(f"health check loop failed: {e}")
        finally:
            db.close()
        await asyncio.sleep(30)
        



app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(auth.router,prefix="/auth")
app.include_router(admin.router,prefix="/admin",dependencies=[Depends(get_session_user)])
app.include_router(analytics.router ,prefix="/analytics", dependencies=[Depends(get_session_user)])


@app.get("/", response_class=HTMLResponse)
def landing_page(request: Request):
    return templates.TemplateResponse(request, "index.html")

templates = Jinja2Templates(directory="app/templates")

# Jinja2 filter for timezone conversion to IST
def to_ist_time(dt):
    """Convert UTC datetime to IST (UTC+5:30) in HH:MM:SS format"""
    if dt is None:
        return "N/A"
    try:
        from datetime import timedelta, timezone
        ist = timezone(timedelta(hours=5, minutes=30))
        # If dt is naive, assume it's UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        ist_time = dt.astimezone(ist)
        return ist_time.strftime('%H:%M:%S')
    except:
        return str(dt)

def to_ist_simple(dt):
    """Convert UTC datetime to IST in simple readable format (e.g., 'Feb 12, 3:45 PM')"""
    if dt is None:
        return "N/A"
    try:
        from datetime import timedelta, timezone
        ist = timezone(timedelta(hours=5, minutes=30))
        # If dt is naive, assume it's UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        ist_time = dt.astimezone(ist)
        return ist_time.strftime('%b %d, %I:%M %p')
    except:
        return str(dt)

templates.env.filters['to_ist_time'] = to_ist_time
templates.env.filters['to_ist_simple'] = to_ist_simple

@app.get('/dashboard')
def dashboard(request: Request , db: Session = Depends(get_db) , current_user: User = Depends(get_session_user)):
    services = None
    excluded_prefixes = ["/admin", "/analytics", "/auth","/static","/dashboard","/health","/favicon.ico"]
    logs = db.query(RequestLog)
    for prefix in excluded_prefixes:
        logs = logs.filter(~RequestLog.path.startswith(prefix))
    if current_user.role == "admin":
        services = db.query(Service).all()
        logs = logs.order_by(RequestLog.timestamp.desc()).limit(10).all()
    else:
        services = db.query(Service).filter(Service.owner_id == current_user.id).all()
        logs = logs.filter(RequestLog.user_id == current_user.id).order_by(RequestLog.timestamp.desc()).limit(10).all()
    response = templates.TemplateResponse(
        request,
        "dashboard.html",
        { "services":services ,
          "logs": logs,
          "user": current_user}
    )
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

app.include_router(proxy.router ,dependencies=[Depends(get_current_user)])

@app.middleware("http")
async def log_requests(request: Request, call_next):
    body = await request.body()
    async def receive():
        return {"type": "http.request", "body": body}
    request._receive = receive
    start_time = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception as e:
        import traceback
        print("App Crashed")
        traceback.print_exc()
        return JSONResponse(status_code=500,content={"detail":str(e)})
    process_time = time.perf_counter() - start_time
    resp_body_bytes = b""
    if hasattr(response,"body_iterator"):
        try:
            response_body = [section async for section in response.body_iterator]
            response.body_iterator = iterate_in_threadpool(iter(response_body))
            resp_body_bytes = b"".join(response_body)
        except Exception as e:
            print(f"Iterator error:{e}")
            resp_body_bytes = b"Could not capture the streaming body"
    else :
        resp_body_bytes = getattr(response,"body",b"")

    db = sessionLocal()
    
    try:
        user = getattr(request.state,"user",None)
        req_text = body.decode('utf-8', errors='ignore')[:2000]
        res_text = resp_body_bytes.decode('utf-8', errors='ignore')[:2000]
        excluded_paths = ["/admin", "/auth", "/dashboard", "/static", "/docs", "/openapi.json"]
        if not any(request.url.path.startswith(p) for p in excluded_paths):
            new_log = RequestLog(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                latency=process_time,
                user_id=user.id if user else None,
                request_body=req_text,
                response_body=res_text
            )
            db.add(new_log)
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error logging request: {e}")
    finally:
        db.close()
    
    print(f"Method: {request.method} | Status: {response.status_code} | Latency: {process_time:.4f} seconds")
    return Response(
        content=resp_body_bytes,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"Critical error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Gateway Error: The requested service is unreachable or misconfigured."},
    )