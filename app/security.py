import hashlib
import bcrypt 

def get_hashed_key(key: str):
    sha_hashed_key = hashlib.sha256(key.encode()).hexdigest().encode()
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(sha_hashed_key, salt)
    return hashed.decode('utf-8')

def verify_api_key(plain_key: str, hashed_key: str):
    sha_hashed_key = hashlib.sha256(plain_key.encode()).hexdigest().encode()
    return bcrypt.checkpw(sha_hashed_key, hashed_key.encode('utf-8'))

    
if __name__ == "__main__":
   myhash = verify_api_key("test", get_hashed_key("test"))
   print(get_hashed_key("test"))
   print(myhash)