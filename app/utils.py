import httpx
from sqlalchemy.orm import Session
from fastapi import Depends , requests, HTTPException
from .database import get_db
from .models import Service
from datetime import datetime,UTC
async def monitor_services(db: Session):
    services = db.query(Service).all()
    async with httpx.AsyncClient() as client:
        for service in services:
            try:
                response = await client.get(f"{service.target_url}/health",timeout=2.0)
                service.is_healthy = response.status_code == 200
            except Exception:
                service.is_healthy = False
            service.last_checked = datetime.now(UTC)
            db.add(service)
        db.commit()

    
