from fastapi import APIRouter , Depends
from ..dependencies import get_current_user
from ..database import get_db
from ..schemas import ServiceCreate,ServiceResponse
from sqlalchemy.orm import Session
from ..models import Service, User
router = APIRouter()
@router.post("/services", response_model=ServiceResponse)
def create_service(service_data: ServiceCreate ,db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_service = Service(**service_data.model_dump())
    new_service.owner_id = current_user.id
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return new_service

@router.get("/services")
def list_services(db: Session = Depends(get_db) , current_user: User = Depends(get_current_user)):
    if current_user.role == "admin":
        return db.query(Service).all()
    return db.query(Service).filter(Service.owner_id == current_user.id).all()