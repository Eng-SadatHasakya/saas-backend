import os
import redis
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Redis connection
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)

def cache_set(key: str, value: dict, expire: int = 300):
    """Cache a value with expiry in seconds (default 5 minutes)"""
    try:
        redis_client.setex(key, expire, json.dumps(value))
        logger.info(f"Cache SET: {key}")
    except Exception as e:
        logger.warning(f"Cache SET failed: {e}")

def cache_get(key: str) -> dict | None:
    """Get cached value"""
    try:
        data = redis_client.get(key)
        if data:
            logger.info(f"Cache HIT: {key}")
            return json.loads(data)
        logger.info(f"Cache MISS: {key}")
        return None
    except Exception as e:
        logger.warning(f"Cache GET failed: {e}")
        return None

def cache_delete(key: str):
    """Delete cached value"""
    try:
        redis_client.delete(key)
        logger.info(f"Cache DELETE: {key}")
    except Exception as e:
        logger.warning(f"Cache DELETE failed: {e}")

def cache_delete_pattern(pattern: str):
    """Delete all keys matching pattern"""
    try:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
            logger.info(f"Cache DELETE pattern: {pattern} ({len(keys)} keys)")
    except Exception as e:
        logger.warning(f"Cache DELETE pattern failed: {e}")

def get_cache_key(prefix: str, org_id: int) -> str:
    """Generate consistent cache key"""
    return f"{prefix}:org:{org_id}"