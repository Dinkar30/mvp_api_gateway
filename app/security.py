import hashlib
import bcrypt 
import jwt
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
load_dotenv()
def get_hashed_key(key: str):
    sha_hashed_key = hashlib.sha256(key.encode()).hexdigest().encode()
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(sha_hashed_key, salt)
    return hashed.decode('utf-8')

def verify_api_key(plain_key: str, hashed_key: str):
    sha_hashed_key = hashlib.sha256(plain_key.encode()).hexdigest().encode()
    return bcrypt.checkpw(sha_hashed_key, hashed_key.encode('utf-8'))

SECRET_KEY = os.getenv("SECRET_KEY", "IseeDeadPeople")
ALGORITHM = "HS256"

def create_access_token(data: dict):
    to_be_encoded = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_be_encoded.update({"exp": expire})
    encoded_jwt = jwt.encode(to_be_encoded, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

    
if __name__ == "__main__":
    access_token = create_access_token({"sub": "testing"})
    print(f"Access Token: {access_token}")
#    myhash = verify_api_key("test", get_hashed_key("test"))
#    print(get_hashed_key("test"))
#    print(myhash)