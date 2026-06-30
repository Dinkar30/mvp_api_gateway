from httpx import AsyncClient, ConnectError
from fastapi import APIRouter,Depends, HTTPException ,Response
from ..models import User , Service
from ..dependencies import get_current_user
from ..database import get_db
from sqlalchemy.orm import Session
router = APIRouter()


@router.get("/{service_prefix}/{path:path}")
async def proxy( service_prefix: str , path: str , db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    service = db.query(Service).filter(Service.prefix == service_prefix).first()
    if not service:
        raise HTTPException(status_code=404 , detail="Service not registered")
    try:
        async with AsyncClient() as client:
            response = await client.get(f"{service.target_url}/{path}" , timeout=5.0)
        return Response(
            content = response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    except ConnectError:
        raise HTTPException(status_code=502,detail=f"could not connect to backend service at {service.target_url}")
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"proxy error: {str(e)}")
    
@router.get("/backend/health")
async def backend_health():
    async with AsyncClient() as client:
        response = await client.get("http://localhost:8001/health")
    return response.json()

