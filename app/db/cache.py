import os
import redis.asyncio as redis
from functools import wraps
from typing import Optional, Any
from app.settings.log import get_logger

LOG = get_logger(__name__)

redis_client: redis.Redis = None

class CacheTTL:
    BALANCE = 60
    CONFIGS = 600
    SUB_END = 3600
    LANG = 86400
    NOTIFICATIONS = 3600
    NODE_METRICS = 120


async def init_cache():
    global redis_client
    if redis_client is None:
        try:
            url = os.getenv("REDIS_URL", "redis://localhost")
            redis_client = await redis.from_url(
                url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
                health_check_interval=30,
                retry_on_timeout=True,
                max_connections=10
            )
            await redis_client.ping()
            LOG.info("Redis connected")
        except Exception as e:
            LOG.error(f"Redis init error: {e}")
            raise


async def get_redis() -> redis.Redis:
    if redis_client is None:
        raise RuntimeError("Redis not initialized. Call init_cache() first.")
    return redis_client


async def close_cache():
    global redis_client
    if redis_client is not None:
        await redis_client.close()
        LOG.info("Redis closed")
        redis_client = None


def safe_redis(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            LOG.warning(f"Redis error in {func.__name__}: {type(e).__name__}: {e}")
            return None
    return wrapper


@safe_redis
async def invalidate_cache(key: str) -> Optional[int]:
    redis = await get_redis()
    return await redis.delete(key)


@safe_redis
async def invalidate_user_cache(tg_id: int, *cache_types: str) -> None:
    redis = await get_redis()
    
    if not cache_types:
        cache_types = ('balance', 'configs', 'sub_end', 'lang', 'notifications')
    
    keys_to_delete = [f"user:{tg_id}:{cache_type}" for cache_type in cache_types]
    
    if keys_to_delete:
        await redis.delete(*keys_to_delete)


@safe_redis
async def set_cache(key: str, value: str, ttl: Optional[int] = None) -> Optional[bool]:
    redis = await get_redis()
    if ttl:
        return await redis.setex(key, ttl, value)
    else:
        return await redis.set(key, value)


@safe_redis
async def get_cache(key: str) -> Optional[str]:
    redis = await get_redis()
    return await redis.get(key)