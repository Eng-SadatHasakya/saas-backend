from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.subscription import Subscription
from app import schemas
from app.services.auth import get_current_user, require_admin
from datetime import datetime, timedelta

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

# Auto-create free subscription when org registers
def create_default_subscription(db: Session, org_id: int):
    # ✅ Check if subscription already exists
    existing = db.query(Subscription).filter(
        Subscription.organization_id == org_id
    ).first()
    if existing:
        return existing

    subscription = Subscription(
        organization_id=org_id,
        plan="free",
        status="active"
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription

# 🔒 Get MY organization's subscription
@router.get("/me", response_model=schemas.SubscriptionResponse)
def get_my_subscription(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    sub = db.query(Subscription).filter(
        Subscription.organization_id == current_user["org_id"]
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="No subscription found")
    return sub

# 🔒 Admin only — upgrade/downgrade plan
@router.put("/me", response_model=schemas.SubscriptionResponse)
def update_subscription(
    data: schemas.SubscriptionUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    valid_plans = ["free", "pro", "enterprise"]
    if data.plan not in valid_plans:
        raise HTTPException(status_code=400, detail=f"Invalid plan. Choose from: {valid_plans}")

    sub = db.query(Subscription).filter(
        Subscription.organization_id == current_user["org_id"]
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="No subscription found")

    sub.plan = data.plan
    sub.updated_at = datetime.now()

    if data.plan in ["pro", "enterprise"]:
        sub.expires_at = datetime.now() + timedelta(days=30)
    else:
        sub.expires_at = None

    db.commit()
    db.refresh(sub)
    return sub