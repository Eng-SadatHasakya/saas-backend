from app.websocket.manager import manager
from app.websocket.events import create_event, EventType
from app.models.notification import Notification
from sqlalchemy.orm import Session

async def emit_and_save(org_id: int, event_type: EventType, message: str, db: Session = None):
    event = create_event(event_type, {"message": message}, org_id)

    # Save to database
    if db:
        notification = Notification(
            organization_id=org_id,
            message=message,
            event_type=event_type
        )
        db.add(notification)
        db.commit()

    # Broadcast via WebSocket
    await manager.broadcast_to_org(org_id, event)

async def emit_user_created(org_id: int, user_data: dict, db: Session = None):
    await emit_and_save(
        org_id,
        EventType.USER_CREATED,
        f"New user {user_data['name']} joined the organization",
        db
    )

async def emit_user_deleted(org_id: int, user_id: int, db: Session = None):
    await emit_and_save(
        org_id,
        EventType.USER_DELETED,
        f"User {user_id} was removed from the organization",
        db
    )

async def emit_invite_sent(org_id: int, email: str, db: Session = None):
    await emit_and_save(
        org_id,
        EventType.INVITE_SENT,
        f"Invite sent to {email}",
        db
    )

async def emit_subscription_updated(org_id: int, plan: str, db: Session = None):
    await emit_and_save(
        org_id,
        EventType.SUBSCRIPTION_UPDATED,
        f"Subscription upgraded to {plan} plan",
        db
    )