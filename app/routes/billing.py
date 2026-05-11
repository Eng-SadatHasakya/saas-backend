from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.core.config import settings
from app.models.subscription import Subscription
from app.models.organization import Organization
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

router = APIRouter(prefix="/billing", tags=["Billing"])

PLAN_PRICES = {
    "pro": settings.STRIPE_PRO_PRICE_ID,
    "enterprise": settings.STRIPE_ENTERPRISE_PRICE_ID,
}

# 🔒 Create checkout session
@router.post("/checkout/{plan}")
def create_checkout_session(
    plan: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    if plan not in PLAN_PRICES:
        raise HTTPException(status_code=400, detail="Invalid plan. Choose pro or enterprise")

    org = db.query(Organization).filter(
        Organization.id == current_user["org_id"]
    ).first()

    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": PLAN_PRICES[plan],
                "quantity": 1,
            }],
            mode="subscription",
            success_url="http://localhost:3000/billing/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://localhost:3000/billing/cancel",
            metadata={
                "org_id": current_user["org_id"],
                "plan": plan,
                "org_name": org.name
            }
        )
        return {
            "checkout_url": session.url,
            "session_id": session.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🔒 Get billing info
@router.get("/info")
def get_billing_info(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    sub = db.query(Subscription).filter(
        Subscription.organization_id == current_user["org_id"]
    ).first()

    return {
        "plan": sub.plan if sub else "free",
        "status": sub.status if sub else "active",
        "expires_at": sub.expires_at if sub else None,
        "publishable_key": settings.STRIPE_PUBLISHABLE_KEY
    }

# Webhook handler
@router.post("/webhook")
async def webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Handle checkout completed
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        org_id = int(session["metadata"]["org_id"])
        plan = session["metadata"]["plan"]

        sub = db.query(Subscription).filter(
            Subscription.organization_id == org_id
        ).first()

        if sub:
            sub.plan = plan
            sub.status = "active"
            db.commit()

    return {"status": "ok"}