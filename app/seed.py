import secrets 
import time
import string
from app.database import engine , Base, sessionLocal
from app.models import APIKey, User , Service
from app.security import get_hashed_key
from datetime import UTC, datetime

def seed():
    Base.metadata.create_all(bind=engine)
    db = sessionLocal()
    try:
        user = User(username= f"user_{int(time.time())}")
        user.rate_limit = 15
        alphabets = string.ascii_letters + string.digits
        password = "".join(secrets.choice(alphabets) for _ in range(16))
        user.hashed_password = get_hashed_key(password)
        db.add(user)
        # print("Before commit:", user.id)
        db.commit()
        db.flush()

        plain_key = f"gw_{secrets.token_urlsafe(32)}"
        hashed_key = get_hashed_key(plain_key)
        api_key_record = APIKey(user_id=user.id , hashed_key=hashed_key)
        db.add(api_key_record)        

        service = Service(name="goDaddy",prefix="goDaddy",target_url="http://backend-service:8001",is_healthy=True, last_checked=datetime.now(UTC))
        db.add(service)

        db.commit()

        print(f"User created:  {user.id},{user.username}")
        print(f"Password for user: {password}")
        print(f"API key generated: {plain_key}")
        print(f"service has been generated: {service}")
        print("keep key safe , won't be shown again")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()
    



if __name__=="__main__":
    seed()