import redis
from .config import get_settings

settings = get_settings()

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    decode_responses=True,
    socket_timeout=5,
    retry_on_timeout=True
)

def get_redis():
    return redis_client 