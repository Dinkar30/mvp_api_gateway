from sqlalchemy.orm import Session
from fastapi import Header , HTTPException , Depends , Request 
from .database import get_db
from .models import APIKey,User
from .security import verify_api_key
from .redis_client import redis_client
import hashlib
async def get_current_user( request: Request, db: Session = Depends(get_db) , x_api_key:str = Header(None)):
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )
    cache_key = f"auth:{hashlib.sha256(x_api_key.encode()).hexdigest()}"
    user = None
    is_user_id_cached = redis_client.get(cache_key)
    if is_user_id_cached:
        user = db.get(User, int(is_user_id_cached))
    else:
        keys = db.query(APIKey).filter(APIKey.is_active==True).all()
        for key in keys:
            if verify_api_key(x_api_key , key.hashed_key):
                user = key.user
                redis_client.setex(cache_key,300,user.id) # just for 5 minutes
                break
    if not user:
            raise HTTPException(
                status_code=403,
                detail="Invalid API key"
            )
    request.state.user = user
    usage_key = f"usage:{user.id}"
    count = redis_client.incr(usage_key)
    if count == 1:
        redis_client.expire(usage_key,60)
    print(f"User {user.id} has used {count} requests this minute.")
    if count>user.rate_limit:
        raise HTTPException(
            status_code=429,
            detail="Too many requests , try later"
        )
    return user

    

