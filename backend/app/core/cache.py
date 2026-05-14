from redis import Redis
from dotenv import load_dotenv
import os

load_dotenv()

redis_client = Redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    decode_responses=True
)