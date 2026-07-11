import secrets
from fastapi import APIRouter , Depends, HTTPException
from ..security import get_hashed_key
from ..dependencies import get_session_user
from ..database import get_db
from ..schemas import ServiceCreate,ServiceResponse
from sqlalchemy.orm import Session
from ..models import APIKey, RequestLog, Service, User
router = APIRouter()
@router.post("/services", response_model=ServiceResponse)
def create_service(service_data: ServiceCreate ,db: Session = Depends(get_db), current_user: User = Depends(get_session_user)):
    new_service = Service(**service_data.model_dump() , owner_id = current_user.id)
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return new_service

@router.get("/services")
def list_services(db: Session = Depends(get_db) , current_user: User = Depends(get_session_user)):
    if current_user.role == "admin":
        return db.query(Service).all()
    return db.query(Service).filter(Service.owner_id == current_user.id).all() 

@router.post("/keys/generate")
def generate_key(db: Session = Depends(get_db), current_user: User = Depends(get_session_user)):
    plain_key = f"gw_{secrets.token_urlsafe(32)}"
    hashed_key = get_hashed_key(plain_key)
    api_key_record = APIKey(user_id=current_user.id , hashed_key=hashed_key)
    db.add(api_key_record)     
    db.commit()
    return {"api_key": plain_key}

@router.delete("/logs/clear")
def clear_logs(db: Session = Depends(get_db), current_user: User = Depends(get_session_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403)
    db.query(RequestLog).delete()
    db.commit()
    return {"message" "all logs cleared"}
    
@router.delete("/services/{service_id}")
def delete_service(service_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_session_user)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    if current_user.role != "admin" and service.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this service")
    db.delete(service)
    db.commit()
    return {"message": "Service deleted successfully"}