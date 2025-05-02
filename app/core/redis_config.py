"""Redis configuration for the application."""

import json
import logging
from typing import Dict, Any, Optional, Union, cast, Protocol, runtime_checkable
import redis.asyncio as redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

@runtime_checkable
class AsyncRedisProtocol(Protocol):
    """Protocol for async Redis client."""
    async def get(self, name: str) -> Optional[str]: ...
    async def set(
        self,
        name: str,
        value: Union[str, bytes],
        ex: Optional[int] = None,
        px: Optional[int] = None,
        nx: bool = False,
        xx: bool = False,
        keepttl: bool = False,
        get: bool = False,
        exat: Optional[int] = None,
        pxat: Optional[int] = None,
    ) -> Optional[bool]: ...
    async def delete(self, *names: str) -> int: ...
    async def flushdb(self, asynchronous: bool = False) -> bool: ...

class RedisClient:
    """Redis client wrapper with type hints and error handling."""
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        """Initialize Redis client."""
        self._client: redis.Redis[str] = redis.Redis(host=host, port=port, db=db, decode_responses=True)
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis."""
        try:
            return await self._client.get(key)
        except RedisError as e:
            logger.error(f"Redis get error: {str(e)}")
            return None
    
    async def set(self, key: str, value: Union[str, bytes], expire: int = 3600) -> bool:
        """Set value in Redis with expiration."""
        try:
            result = await self._client.set(key, value, ex=expire)
            return bool(result) if result is not None else False
        except RedisError as e:
            logger.error(f"Redis set error: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        try:
            result = await self._client.delete(key)
            return bool(result)
        except RedisError as e:
            logger.error(f"Redis delete error: {str(e)}")
            return False
    
    async def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        """Get JSON value from Redis."""
        try:
            value = await self._client.get(key)
            if value is None:
                return None
            return cast(Dict[str, Any], json.loads(value))
        except (RedisError, json.JSONDecodeError) as e:
            logger.error(f"Redis get_json error: {str(e)}")
            return None
    
    async def set_json(self, key: str, value: Dict[str, Any], expire: int = 3600) -> bool:
        """Set JSON value in Redis with expiration."""
        try:
            result = await self._client.set(key, json.dumps(value), ex=expire)
            return bool(result) if result is not None else False
        except (RedisError, TypeError) as e:
            logger.error(f"Redis set_json error: {str(e)}")
            return False
    
    async def flushdb(self) -> bool:
        """Flush all keys from the current database."""
        try:
            await self._client.flushdb()
            return True
        except RedisError as e:
            logger.error(f"Redis flushdb error: {str(e)}")
            return False

# Create a global Redis client instance
redis_client = RedisClient()
