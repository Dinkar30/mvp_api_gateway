from fastapi import Depends , APIRouter
from httpx import AsyncClient
from sqlalchemy import func 
from sqlalchemy.orm import Session
from app.models import RequestLog
from ..database import get_db 
import time 
router = APIRouter()
@router.get("/total-requests")
async def total_requests(db: Session = Depends(get_db)):
    try:
        total = db.query(RequestLog).count()
        return {"total requests": total}
    except Exception as e:
        print(f"Error fetching total requests: {e}")
        return {"error": "Could not fetch total requests"}


@router.get("/request-per-route")
async def request_per_route(db: Session = Depends(get_db)):
    try:
        results = db.query(RequestLog.path, func.count(RequestLog.id)).group_by(RequestLog.path).all()
        return {path: count for path, count in results}
    except Exception as e:
        print(f"Error fetching requests per route: {e}")
        return {"error": "Could not fetch requests per route"}


@router.get("/average-latency")
async def average_latency(db: Session = Depends(get_db)):
    try:
        results = db.query(RequestLog.path, func.avg(RequestLog.latency)).group_by(RequestLog.path).all()
        return {path: avg_latency for path, avg_latency in results}
    except Exception as e:
        print(f"Error fetching average latency: {e}")
        return {"error": "Could not fetch average latency"}




@router.get("/error-rate")
def error_rate(db: Session = Depends(get_db)):
    try:
        total_requests = db.query(RequestLog).count()
        error_requests = db.query(RequestLog).filter(RequestLog.status_code >= 400).count()
        error_rate = (error_requests / total_requests) * 100 if total_requests > 0 else 0
        return {"total_requests": total_requests, "error_count": error_requests, "error_rate": f"{error_rate:.2f}%"}
    except Exception as e:
        print(f"Error calculating error rate: {e}")
        return {"error": "Could not calculate error rate"}