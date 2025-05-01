from typing import Optional, Any
import redis
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RedisConfig:
    def __init__(self):
        """Initialize Redis client with configuration from environment variables."""
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            password=os.getenv('REDIS_PASSWORD', None),
            db=0,
            decode_responses=True,
            socket_timeout=5,
            retry_on_timeout=True
        )
        self._test_connection()

    def _test_connection(self) -> None:
        """Test Redis connection and raise an error if connection fails."""
        try:
            self.redis_client.ping()
        except redis.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to Redis: {str(e)}")

    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis."""
        try:
            return self.redis_client.get(key)
        except redis.RedisError as e:
            print(f"Error getting key {key} from Redis: {str(e)}")
            return None

    def set(self, key: str, value: Any, expiration: int = None) -> bool:
        """Set value in Redis with optional expiration in seconds."""
        try:
            return self.redis_client.set(key, value, ex=expiration)
        except redis.RedisError as e:
            print(f"Error setting key {key} in Redis: {str(e)}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        try:
            return bool(self.redis_client.delete(key))
        except redis.RedisError as e:
            print(f"Error deleting key {key} from Redis: {str(e)}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        try:
            return bool(self.redis_client.exists(key))
        except redis.RedisError as e:
            print(f"Error checking existence of key {key} in Redis: {str(e)}")
            return False

    def clear_cache(self) -> bool:
        """Clear all keys in the current database."""
        try:
            return bool(self.redis_client.flushdb())
        except redis.RedisError as e:
            print(f"Error clearing Redis cache: {str(e)}")
            return False

# Create a singleton instance
redis_client = RedisConfig() 