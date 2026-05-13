from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.platform import PlatformService
from app.core.cache import cache_get, cache_set, cache_delete, get_cache_key

router = APIRouter(prefix="/platform", tags=["Platform"])

@router.get("/summary")
def get_platform_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    org_id = current_user["org_id"]
    cache_key = get_cache_key("platform_summary", org_id)

    # ✅ Try cache first
    cached = cache_get(cache_key)
    if cached:
        cached["cached"] = True
        return cached

    # Cache miss — fetch from DB
    service = PlatformService(
        db=db,
        org_id=org_id,
        user_role=current_user["role"]
    )
    summary = service.get_platform_summary()

    # ✅ Save to cache for 5 minutes
    cache_set(cache_key, summary, expire=300)

    summary["cached"] = False
    return summary

@router.delete("/cache")
def clear_cache(current_user: dict = Depends(get_current_user)):
    """Clear cache for current org"""
    org_id = current_user["org_id"]
    cache_delete(get_cache_key("platform_summary", org_id))
    return {"message": "Cache cleared"}

@router.get("/health")
def platform_health(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    service = PlatformService(
        db=db,
        org_id=current_user["org_id"],
        user_role=current_user["role"]
    )
    context = service.get_org_context()
    return {
        "status": "healthy",
        "tenant": context["org_name"],
        "users": context["total_users"],
        "plan": context["plan"],
    }