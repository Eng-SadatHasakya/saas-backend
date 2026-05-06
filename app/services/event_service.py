from app.websocket.manager import manager
from app.websocket.events import create_event, EventType
from app.models.notification import Notification
from app.core.platform import PlatformService
from app.websocket.events import EventType
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
    if db:
        service = PlatformService(db=db, org_id=org_id, user_role="system")
        await service.emit_event(
            EventType.USER_CREATED,
            f"New user {user_data['name']} joined the organization"
        )

async def emit_user_deleted(org_id: int, user_id: int, db: Session = None):
    if db:
        service = PlatformService(db=db, org_id=org_id, user_role="system")
        await service.emit_event(
            EventType.USER_DELETED,
            f"User {user_id} was removed from the organization"
        )

async def emit_invite_sent(org_id: int, email: str, db: Session = None):
    if db:
        service = PlatformService(db=db, org_id=org_id, user_role="system")
        await service.emit_event(
            EventType.INVITE_SENT,
            f"Invite sent to {email}"
        )

async def emit_subscription_updated(org_id: int, plan: str, db: Session = None):
    if db:
        service = PlatformService(db=db, org_id=org_id, user_role="system")
        await service.emit_event(
            EventType.SUBSCRIPTION_UPDATED,
            f"Subscription upgraded to {plan} plan"
        )

async def emit_user_created(org_id: int, user_data: dict):
    event = create_event(
        EventType.USER_CREATED,
        {"message": f"New user {user_data['name']} joined the organization", "user": user_data},
        org_id
    )
    await manager.broadcast_to_org(org_id, event)

async def emit_user_deleted(org_id: int, user_id: int):
    event = create_event(
        EventType.USER_DELETED,
        {"message": f"User {user_id} was removed from the organization"},
        org_id
    )
    await manager.broadcast_to_org(org_id, event)

async def emit_invite_sent(org_id: int, email: str):
    event = create_event(
        EventType.INVITE_SENT,
        {"message": f"Invite sent to {email}"},
        org_id
    )
    await manager.broadcast_to_org(org_id, event)

async def emit_subscription_updated(org_id: int, plan: str):
    event = create_event(
        EventType.SUBSCRIPTION_UPDATED,
        {"message": f"Subscription upgraded to {plan} plan"},
        org_id
    )
    await manager.broadcast_to_org(org_id, event)

async def emit_ai_response(org_id: int, query: str, response: str):
    event = create_event(
        EventType.AI_RESPONSE_READY,
        {"query": query, "response": response},
        org_id
    )
    await manager.broadcast_to_org(org_id, event)