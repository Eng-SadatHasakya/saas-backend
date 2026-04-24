from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.models.organization import Organization
from app.models.subscription import Subscription
from app.models.invitation import Invitation
from app.models.api_key import APIKey
from app.services.auth import get_current_user
from app.ai.service import ask_ai
from app.ai.prompts import build_system_prompt, build_user_prompt

router = APIRouter(prefix="/ai", tags=["AI Assistant"])

class AIQuery(BaseModel):
    query: str

@router.post("/query")
def ai_query(
    data: AIQuery,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    org_id = current_user["org_id"]

    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    users = db.query(User).filter(User.organization_id == org_id).all()
    sub = db.query(Subscription).filter(Subscription.organization_id == org_id).first()
    pending_invites = db.query(Invitation).filter(
        Invitation.organization_id == org_id,
        Invitation.accepted == False
    ).count()
    active_keys = db.query(APIKey).filter(
        APIKey.organization_id == org_id,
        APIKey.is_active == True
    ).count()

    users_list = "\n".join([
        f"- {u.name} ({u.email}) | Role: {u.role} | Joined: {u.created_at.strftime('%Y-%m-%d')}"
        for u in users
    ])

    context = {
        "org_name": org.name,
        "total_users": len(users),
        "plan": sub.plan if sub else "none",
        "status": sub.status if sub else "none",
        "users_list": users_list or "No users found",
        "pending_invites": pending_invites,
        "active_keys": active_keys,
    }

    system_prompt = build_system_prompt(org.name, current_user["role"])
    user_prompt = build_user_prompt(data.query, context)
    response = ask_ai(system_prompt, user_prompt)

    return {
        "query": data.query,
        "response": response,
        "organization": org.name
    }