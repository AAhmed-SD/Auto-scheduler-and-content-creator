from redis import Redis
from typing import Optional
import json
import os
from datetime import timedelta

class RedisConfig:
    def __init__(self):
        self.redis_host = os.getenv('REDIS_HOST', 'localhost')
        self.redis_port = int(os.getenv('REDIS_PORT', 6379))
        self.redis_password = os.getenv('REDIS_PASSWORD', None)
        self.redis_db = int(os.getenv('REDIS_DB', 0))
        
        self.redis_client = Redis(
            host=self.redis_host,
            port=self.redis_port,
            password=self.redis_password,
            db=self.redis_db,
            decode_responses=True
        )

    def get(self, key: str) -> Optional[dict]:
        """Get value from Redis cache"""
        value = self.redis_client.get(key)
        return json.loads(value) if value else None

    def set(self, key: str, value: dict, expire: int = 3600) -> bool:
        """Set value in Redis cache with expiration"""
        return self.redis_client.setex(
            key,
            timedelta(seconds=expire),
            json.dumps(value)
        )

    def delete(self, key: str) -> bool:
        """Delete value from Redis cache"""
        return bool(self.redis_client.delete(key))

    def exists(self, key: str) -> bool:
        """Check if key exists in Redis cache"""
        return bool(self.redis_client.exists(key))

    def clear_cache(self) -> bool:
        """Clear all cache"""
        return bool(self.redis_client.flushdb())

# Create global Redis instance
redis = RedisConfig() 