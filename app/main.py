from fastapi import FastAPI,Request , Depends
from .models import RequestLog
from .database import engine, Base,sessionLocal
import time
from .routers import analytics, proxy, admin
from .dependencies import get_current_user
app = FastAPI()

Base.metadata.create_all(bind=engine)
app.include_router(admin.router,prefix="/admin",dependencies=[Depends(get_current_user)])
app.include_router(analytics.router ,prefix="/analytics", dependencies=[Depends(get_current_user)])
app.include_router(proxy.router ,dependencies=[Depends(get_current_user)])



@app.get("/")
async def root():
    return {"message": "the gateway is working"}   


@app.get("/health")
async def health():
    return {"status": "healthy"}


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
