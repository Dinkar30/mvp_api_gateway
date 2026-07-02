from fastapi import APIRouter , Depends, HTTPException
from sqlalchemy.orm import Session
from ..security import create_access_token, verify_api_key
from ..database import get_db
from ..schemas import UserLogin
from ..models import User

router = APIRouter()

@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
  try:
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_api_key(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer", "user_id": user.id}
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))