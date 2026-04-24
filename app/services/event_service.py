from app.websocket.manager import manager
from app.websocket.events import create_event, EventType

async def emit_user_created(org_id: int, user_data: dict):
    event = create_event(
        EventType.USER_CREATED,
        {
            "message": f"New user {user_data['name']} joined the organization",
            "user": user_data
        },
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