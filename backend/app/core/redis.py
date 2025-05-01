import redis
import logging
import time
from typing import Optional, Any, Dict
from redis.exceptions import ConnectionError, RedisError

from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self._max_retries = 3
        self._retry_delay = 1  # seconds

    def get_client(self) -> redis.Redis:
        """Get Redis client with retry mechanism"""
        if self._client is not None:
            return self._client

        retries = 0
        while retries < self._max_retries:
            try:
                self._client = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    password=settings.REDIS_PASSWORD,
                    db=settings.REDIS_DB,
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5
                )
                # Test connection
                self._client.ping()
                return self._client
            except (ConnectionError, RedisError) as e:
                retries += 1
                if retries == self._max_retries:
                    logger.error(f"Failed to connect to Redis after {self._max_retries} attempts: {str(e)}")
                    raise
                logger.warning(f"Redis connection attempt {retries} failed. Retrying in {self._retry_delay}s...")
                time.sleep(self._retry_delay)

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from Redis"""
        try:
            client = self.get_client()
            value = client.get(key)
            return value if value is not None else default
        except RedisError as e:
            logger.error(f"Error getting key {key} from Redis: {str(e)}")
            return default

    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set value in Redis with optional expiration"""
        try:
            client = self.get_client()
            return client.set(key, value, ex=expire)
        except RedisError as e:
            logger.error(f"Error setting key {key} in Redis: {str(e)}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        try:
            client = self.get_client()
            return bool(client.delete(key))
        except RedisError as e:
            logger.error(f"Error deleting key {key} from Redis: {str(e)}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        try:
            client = self.get_client()
            return bool(client.exists(key))
        except RedisError as e:
            logger.error(f"Error checking existence of key {key} in Redis: {str(e)}")
            return False

    def flush(self) -> bool:
        """Flush all keys from Redis"""
        try:
            client = self.get_client()
            client.flushdb()
            return True
        except RedisError as e:
            logger.error(f"Error flushing Redis: {str(e)}")
            return False

    def close(self):
        """Close Redis connection"""
        if self._client is not None:
            try:
                self._client.close()
                self._client = None
            except RedisError as e:
                logger.error(f"Error closing Redis connection: {str(e)}")

# Global Redis client instance
redis_client = RedisClient() 