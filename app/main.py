from fastapi import FastAPI,Request , Depends 
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .routers import auth
from .models import RequestLog, Service, User
from .database import engine, Base,sessionLocal , get_db
from .routers import analytics, proxy, admin
from .dependencies import get_session_user, get_current_user
from sqlalchemy.orm import Session 
from contextlib import asynccontextmanager
from .utils import monitor_services
import time
import asyncio
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(repeat_health_check())
    yield
app = FastAPI(lifespan=lifespan)
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
app.include_router(admin.router,prefix="/admin",dependencies=[Depends(get_current_user)])
app.include_router(analytics.router ,prefix="/analytics", dependencies=[Depends(get_current_user)])


@app.get("/")
async def root():
    return {"message": "the gateway is working"}   

templates = Jinja2Templates(directory="app/templates")

@app.get('/dashboard' , dependencies=[Depends(get_session_user)])
def dashboard(request: Request , db: Session = Depends(get_db) , current_user: User = Depends(get_current_user)):
    services = None
    if current_user.role == "admin":
        services = db.query(Service).all()
    else:
        services = db.query(Service).filter(Service.owner_id == current_user.id).all()

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        { "services":services}
    )

@app.get("/health")
async def health():
    return {"status": "healthy"}

app.include_router(proxy.router ,dependencies=[Depends(get_current_user)])

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    db = sessionLocal()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    user = getattr(request.state,"user",None)
    try:
        new_log = RequestLog(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            latency=process_time,
            user_id=user.id if user else None
        )
        db.add(new_log)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error logging request: {e}")
    finally:
        db.close()
    
    print(f"Method: {request.method} | Status: {response.status_code} | Latency: {process_time:.4f} seconds")
    return response

