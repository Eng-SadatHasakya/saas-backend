from sqlalchemy.orm import Session
from app.models.user import User
from app.models.organization import Organization
from app.models.subscription import Subscription
from app.models.invitation import Invitation
from app.models.api_key import APIKey
from app.models.notification import Notification
from app.core.config import settings
from app.core.ai import ask_ai
from app.ai.prompts import build_system_prompt, build_user_prompt
from app.websocket.manager import manager
from app.websocket.events import create_event, EventType
import logging

logger = logging.getLogger(__name__)

class PlatformService:
    """
    Unified service layer that connects all platform components:
    Auth → Tenant → AI → WebSocket → Notifications → Database
    """

    def __init__(self, db: Session, org_id: int, user_role: str):
        self.db = db
        self.org_id = org_id
        self.user_role = user_role

    def get_org_context(self) -> dict:
        """Get full organization context for AI and analytics"""
        org = self.db.query(Organization).filter(
            Organization.id == self.org_id
        ).first()

        users = self.db.query(User).filter(
            User.organization_id == self.org_id
        ).all()

        sub = self.db.query(Subscription).filter(
            Subscription.organization_id == self.org_id
        ).first()

        pending_invites = self.db.query(Invitation).filter(
            Invitation.organization_id == self.org_id,
            Invitation.accepted == False
        ).count()

        active_keys = self.db.query(APIKey).filter(
            APIKey.organization_id == self.org_id,
            APIKey.is_active == True
        ).count()

        unread_notifications = self.db.query(Notification).filter(
            Notification.organization_id == self.org_id,
            Notification.is_read == False
        ).count()

        users_list = "\n".join([
            f"- {u.name} ({u.email}) | Role: {u.role}"
            for u in users
        ])

        return {
            "org_name": org.name if org else "Unknown",
            "org_id": self.org_id,
            "total_users": len(users),
            "plan": sub.plan if sub else "free",
            "status": sub.status if sub else "active",
            "users_list": users_list or "No users",
            "pending_invites": pending_invites,
            "active_keys": active_keys,
            "unread_notifications": unread_notifications,
        }

    async def process_ai_query(self, query: str) -> str:
        """Process AI query with full org context"""
        context = self.get_org_context()
        system_prompt = build_system_prompt(context["org_name"], self.user_role)
        user_prompt = build_user_prompt(query, context)
        response = ask_ai(system_prompt, user_prompt)
        logger.info(f"AI query processed for org {self.org_id}: {query[:50]}...")
        return response

    async def emit_event(self, event_type: EventType, message: str):
        """Emit real-time event + save to database"""
        # Save to database
        notification = Notification(
            organization_id=self.org_id,
            message=message,
            event_type=event_type
        )
        self.db.add(notification)
        self.db.commit()

        # Broadcast via WebSocket
        event = create_event(event_type, {"message": message}, self.org_id)
        await manager.broadcast_to_org(self.org_id, event)
        logger.info(f"Event {event_type} emitted for org {self.org_id}")

    def get_platform_summary(self) -> dict:
        """Get full platform summary for dashboard"""
        context = self.get_org_context()
        return {
            "organization": context["org_name"],
            "total_users": context["total_users"],
            "plan": context["plan"],
            "pending_invites": context["pending_invites"],
            "active_keys": context["active_keys"],
            "unread_notifications": context["unread_notifications"],
            "platform_version": settings.APP_VERSION,
        }