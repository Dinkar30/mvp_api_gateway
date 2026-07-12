from httpx import AsyncClient, ConnectError, TimeoutException, request
from fastapi import APIRouter,Depends, HTTPException ,Response, Request
from websockets import client, headers
from ..models import User , Service
from ..dependencies import get_current_user
from ..database import get_db
from sqlalchemy.orm import Session
import asyncio

MAX_RETRIES = 3
RETRY_BACKOFF_FACTOR = 0.5  
SAFE_METHODS = {"GET"} 
RETRYABLE_ERRORS = (ConnectError, TimeoutException)

router = APIRouter()


@router.api_route("/{service_prefix}/{path:path}" , methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy( request: Request, service_prefix: str , path: str , db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    service = db.query(Service).filter(Service.prefix == service_prefix).first()
    if not service:
        raise HTTPException(status_code=404 , detail="Service not registered")
    try:
        async with AsyncClient() as client:
            url = f"{service.target_url}/{path}"
            headers = dict(request.headers)
            headers.pop("x-api-key", None)
            headers.pop("host", None)


            for attempt in range(MAX_RETRIES):
                try:
                    response = await client.request(
                        method=request.method,
                        url=url,
                        content=await request.body(),
                        headers=headers,
                        params=request.query_params,
                        timeout=10.0
                    )
                    break
                except RETRYABLE_ERRORS as e:
                    if request.method in SAFE_METHODS and attempt < MAX_RETRIES - 1:
                        backoff_time = RETRY_BACKOFF_FACTOR * (attempt + 1)
                        await asyncio.sleep(backoff_time)
                        continue
                    else:
                        raise
            
            if not service.is_healthy:
                raise HTTPException(status_code=503,detail="service is currently unavailable")
            client_headers = dict(response.headers)
            client_headers.pop("Transfer-Encoding", None)
            client_headers.pop("Content-Length", None)
            client_headers.pop("content-length", None)
            return Response(
                content = response.content,
                status_code=response.status_code,
                headers=client_headers
            )
    except ConnectError:
        raise HTTPException(status_code=502,detail=f"could not connect to backend service at {service.target_url}")
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"proxy error: {str(e)}")
    
