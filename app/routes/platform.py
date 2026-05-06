from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.platform import PlatformService

router = APIRouter(prefix="/platform", tags=["Platform"])

@router.get("/summary")
def get_platform_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Single endpoint that returns complete platform context.
    Frontend calls this once to load everything.
    """
    service = PlatformService(
        db=db,
        org_id=current_user["org_id"],
        user_role=current_user["role"]
    )
    return service.get_platform_summary()

@router.get("/health")
def platform_health(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Check platform health for current tenant"""
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