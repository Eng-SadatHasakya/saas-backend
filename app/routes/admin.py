from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.db_optimizer import get_db_stats, get_index_usage
from app.core.cache import redis_client
import platform
import psutil

router = APIRouter(prefix="/admin", tags=["System Admin"])

@router.get("/db-stats")
def database_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get database table statistics"""
    return {
        "tables": get_db_stats(db),
        "indexes": get_index_usage(db)
    }

@router.get("/cache-stats")
def cache_stats(current_user: dict = Depends(get_current_user)):
    """Get Redis cache statistics"""
    try:
        info = redis_client.info()
        return {
            "connected": True,
            "used_memory": info.get("used_memory_human"),
            "total_keys": redis_client.dbsize(),
            "hits": info.get("keyspace_hits", 0),
            "misses": info.get("keyspace_misses", 0),
            "uptime_seconds": info.get("uptime_in_seconds", 0),
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}

@router.get("/system-stats")
def system_stats(current_user: dict = Depends(get_current_user)):
    """Get system resource statistics"""
    try:
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
            "python_version": platform.python_version(),
            "os": platform.system(),
        }
    except Exception as e:
        return {"error": str(e)}