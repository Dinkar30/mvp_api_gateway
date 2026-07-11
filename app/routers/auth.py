from fastapi import APIRouter , Depends, HTTPException , Request
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from ..security import create_access_token, verify_api_key, get_hashed_key
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
def get_login(request: Request):
   response = templates.TemplateResponse(request,"login.html")
   response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
   response.headers["Pragma"] = "no-cache"
   response.headers["Expires"] = "0"
   return response
   
@router.post("/logout")
def logout():
    response = JSONResponse({"message": "Logout successful"})
    response.delete_cookie(key="access_token", path="/", httponly=True, samesite="lax")
    return response

@router.get("/signup", response_class=HTMLResponse)
def get_signup(request: Request):
    response = templates.TemplateResponse(request, "signup.html")
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@router.post("/signup")
def signup(data: UserLogin, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(User).filter(User.username == data.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        hashed_password = get_hashed_key(data.password)
        new_user = User(
            username=data.username,
            hashed_password=hashed_password
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return JSONResponse({
            "message": "Sign up successful",
            "user_id": new_user.id
        })
    
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))