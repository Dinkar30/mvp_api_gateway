from redis import Redis 
import os
from dotenv import load_dotenv
load_dotenv()
redis_client = Redis(host=os.getenv("REDIS_HOST","localhost"), port=6379, db=0, decode_responses=True)


