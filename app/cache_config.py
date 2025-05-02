"""Cache configuration for the application."""

from typing import Any, Optional, Dict, TypeVar, Callable, cast, Union, Awaitable, overload
from functools import wraps
import json
import logging
import redis.asyncio as redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)
T = TypeVar('T')
CacheResult = Dict[str, Any]

# Cache settings
DEFAULT_TIMEOUT = 300  # 5 minutes
LONG_TIMEOUT = 3600  # 1 hour
EXTENDED_TIMEOUT = 86400  # 24 hours

# Initialize Redis client
redis_client: redis.Redis[str] = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True
)

async def get_cache(key: str) -> Optional[CacheResult]:
    """Get value from cache."""
    try:
        value = await redis_client.get(key)
        if value is None:
            return None
        return cast(CacheResult, json.loads(value))
    except (RedisError, json.JSONDecodeError) as e:
        logger.error(f"Cache get error: {str(e)}")
        return None

async def set_cache(key: str, value: CacheResult, expire: int = DEFAULT_TIMEOUT) -> bool:
    """Set value in cache."""
    try:
        result = await redis_client.set(key, json.dumps(value), ex=expire)
        return bool(result) if result is not None else False
    except (RedisError, TypeError) as e:
        logger.error(f"Cache set error: {str(e)}")
        return False

async def delete_cache(key: str) -> bool:
    """Delete value from cache."""
    try:
        result = await redis_client.delete(key)
        return bool(result)
    except RedisError as e:
        logger.error(f"Cache delete error: {str(e)}")
        return False

@overload
def cache(*, expire: int = DEFAULT_TIMEOUT) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]: ...

@overload
def cache(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]: ...

def cache(
    func: Optional[Callable[..., Awaitable[T]]] = None,
    *,
    expire: int = DEFAULT_TIMEOUT,
) -> Union[
    Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]],
    Callable[..., Awaitable[T]],
]:
    """Cache decorator for async functions."""
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            # Generate cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cached_result = await get_cache(cache_key)
            if cached_result is not None:
                return cast(T, cached_result.get("result", cached_result))
            
            # If not in cache, execute function
            result = await func(*args, **kwargs)
            cache_data: CacheResult = {"result": result} if not isinstance(result, dict) else result
            
            # Store result in cache
            cache_success = await set_cache(cache_key, cache_data, expire)
            if not cache_success:
                logger.warning(f"Failed to cache result for {cache_key}")
            
            return cast(T, cache_data.get("result", cache_data))
        return wrapper
    
    if func is None:
        return decorator
    return decorator(func)

async def get_user_data(user_id: str) -> Optional[CacheResult]:
    """Get user data from cache."""
    key = f"user:{user_id}"
    cached_data = await get_cache(key)
    return cached_data

async def set_user_data(user_id: str, data: CacheResult, expire: int = DEFAULT_TIMEOUT) -> bool:
    """Set user data in cache."""
    key = f"user:{user_id}"
    success = await set_cache(key, data, expire)
    return success

async def delete_user_data(user_id: str) -> bool:
    """Delete user data from cache."""
    key = f"user:{user_id}"
    success = await delete_cache(key)
    return success

def get_project_data(project_id: str) -> Optional[Dict[str, Any]]:
    """Get project data from cache."""
    try:
        data = redis_client.get(f'project:{project_id}')
        if data is None:
            return None
        return json.loads(str(data))
    except redis.RedisError as e:
        logger.error("Error getting project data from cache: %s", str(e))
        return None
    except json.JSONDecodeError as e:
        logger.error("Error decoding project data from cache: %s", str(e))
        return None

def set_project_data(project_id: str, data: Dict[str, Any], timeout: int = DEFAULT_TIMEOUT) -> bool:
    """Set project data in cache."""
    try:
        serialized_data = json.dumps(data)
        redis_client.setex(f'project:{project_id}', timeout, serialized_data)
        return True
    except (redis.RedisError, TypeError) as e:
        logger.error("Error setting project data in cache: %s", str(e))
        return False

def get_content_data(content_id: str) -> Optional[Dict[str, Any]]:
    """Get content data from cache."""
    try:
        data = redis_client.get(f'content:{content_id}')
        if data is None:
            return None
        return json.loads(str(data))
    except redis.RedisError as e:
        logger.error("Error getting content data from cache: %s", str(e))
        return None
    except json.JSONDecodeError as e:
        logger.error("Error decoding content data from cache: %s", str(e))
        return None

def set_content_data(content_id: str, data: Dict[str, Any], timeout: int = DEFAULT_TIMEOUT) -> bool:
    """Set content data in cache."""
    try:
        serialized_data = json.dumps(data)
        redis_client.setex(f'content:{content_id}', timeout, serialized_data)
        return True
    except (redis.RedisError, TypeError) as e:
        logger.error("Error setting content data in cache: %s", str(e))
        return False

def get_team_data(team_id: str) -> Optional[Dict[str, Any]]:
    """Get team data from cache."""
    try:
        data = redis_client.get(f'team:{team_id}')
        if data is None:
            return None
        return json.loads(str(data))
    except redis.RedisError as e:
        logger.error("Error getting team data from cache: %s", str(e))
        return None
    except json.JSONDecodeError as e:
        logger.error("Error decoding team data from cache: %s", str(e))
        return None

def set_team_data(team_id: str, data: Dict[str, Any], timeout: int = DEFAULT_TIMEOUT) -> bool:
    """Set team data in cache."""
    try:
        serialized_data = json.dumps(data)
        redis_client.setex(f'team:{team_id}', timeout, serialized_data)
        return True
    except (redis.RedisError, TypeError) as e:
        logger.error("Error setting team data in cache: %s", str(e))
        return False

def get_agency_data(agency_id: str) -> Optional[Dict[str, Any]]:
    """Get agency data from cache."""
    try:
        data = redis_client.get(f'agency:{agency_id}')
        if data is None:
            return None
        return json.loads(str(data))
    except redis.RedisError as e:
        logger.error("Error getting agency data from cache: %s", str(e))
        return None
    except json.JSONDecodeError as e:
        logger.error("Error decoding agency data from cache: %s", str(e))
        return None

def set_agency_data(agency_id: str, data: Dict[str, Any], timeout: int = DEFAULT_TIMEOUT) -> bool:
    """Set agency data in cache."""
    try:
        serialized_data = json.dumps(data)
        redis_client.setex(f'agency:{agency_id}', timeout, serialized_data)
        return True
    except (redis.RedisError, TypeError) as e:
        logger.error("Error setting agency data in cache: %s", str(e))
        return False

async def clear_cache() -> bool:
    """Clear all cache data."""
    try:
        result = await redis_client.flushdb()
        return bool(result) if result is not None else False
    except RedisError as e:
        logger.error(f"Cache clear error: {str(e)}")
        return False
