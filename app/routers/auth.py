from fastapi import APIRouter , Depends, HTTPException , Request
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from ..security import create_access_token, verify_api_key
from ..database import get_db
from ..schemas import UserLogin
from ..models import User
from fastapi.responses import HTMLResponse, JSONResponse

router = APIRouter()

@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
  try:
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_api_key(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token({"sub": user.username})
    response = JSONResponse({
        "message": "Login successful",
        "user_id": user.id
    })
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=3600
    )
    return response
  
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
  

templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class = HTMLResponse)
def login(request: Request):
   return templates.TemplateResponse(request,"login.html")
   