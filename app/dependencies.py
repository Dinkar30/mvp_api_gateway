from sqlalchemy.orm import Session
from fastapi import Header , HTTPException , Depends , Request 
from .database import get_db
from .models import APIKey
from .security import verify_api_key
from .redis_client import redis_client
RATE_LIMIT=5
async def get_current_user( request: Request, db: Session = Depends(get_db) , x_api_key:str = Header(None)):
    if(x_api_key == None):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )
    keys = db.query(APIKey).filter(APIKey.is_active==True).all()
    is_valid = False
    user = None
    for key in keys:
        if verify_api_key(x_api_key , key.hashed_key):
            user = key.user
            is_valid = True
            request.state.user = user
            break
    if is_valid == False:
        raise HTTPException(status_code=403 , detail="Invalid api key")
    key = f"usage:{user.id}"
    count = redis_client.incr(key)
    if count>user.rate_limit:
        raise HTTPException(
            status_code=429,
            detail="Too many requests , try later"
        )
    if count == 1:
        redis_client.expire(key,60)
    print(f"User {user.id} has used {count} requests this minute.")
    return user
    

