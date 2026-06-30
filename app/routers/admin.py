from fastapi import APIRouter , Depends
from ..database import get_db
from ..schemas import ServiceCreate,ServiceResponse
from sqlalchemy.orm import Session
from ..models import Service
router = APIRouter()
@router.post("/services", response_model=ServiceResponse)
def create_service(service_data: ServiceCreate ,db: Session = Depends(get_db)):
    new_service = Service(**service_data.model_dump())
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return new_service

@router.get("/services")
def list_services(db: Session = Depends(get_db)):
    return db.query(Service).all()
