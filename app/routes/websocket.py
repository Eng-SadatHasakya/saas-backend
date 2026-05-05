from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.websocket.manager import manager
from app.websocket.events import create_event, EventType
from app.core.security import decode_token
from app.core.ai import ask_ai
from app.database import SessionLocal
from app.models.user import User
from app.models.organization import Organization
from app.models.subscription import Subscription
from app.models.invitation import Invitation
from app.models.api_key import APIKey
from app.ai.prompts import build_system_prompt, build_user_prompt
import json

router = APIRouter(tags=["WebSocket"])

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...)
):
    # Authenticate
    try:
        user = decode_token(token)
    except Exception:
        await websocket.close(code=4001)
        return

    org_id = user["org_id"]

    # Connect
    await manager.connect(websocket, org_id)

    # Welcome message
    await manager.send_to_user(websocket, create_event(
        EventType.NOTIFICATION,
        {"message": "Connected to real-time platform"},
        org_id
    ))

    try:
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
            except Exception:
                message = {"type": "chat", "content": data}

            # ✅ Handle AI query via WebSocket
            if message.get("type") == "ai_query":
                query = message.get("content", "")

                # Send thinking indicator
                await manager.send_to_user(websocket, create_event(
                    EventType.AI_THINKING,
                    {"message": "AI is thinking..."},
                    org_id
                ))

                # Fetch org data for context
                db = SessionLocal()
                try:
                    org = db.query(Organization).filter(Organization.id == org_id).first()
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
                        f"- {u.name} ({u.email}) | Role: {u.role}"
                        for u in users
                    ])

                    context = {
                        "org_name": org.name if org else "Unknown",
                        "total_users": len(users),
                        "plan": sub.plan if sub else "free",
                        "status": sub.status if sub else "active",
                        "users_list": users_list or "No users",
                        "pending_invites": pending_invites,
                        "active_keys": active_keys,
                    }
                finally:
                    db.close()

                # Get AI response
                system_prompt = build_system_prompt(
                    context["org_name"],
                    user["role"]
                )
                user_prompt = build_user_prompt(query, context)
                response = ask_ai(system_prompt, user_prompt)

                # Send AI response back
                await manager.send_to_user(websocket, create_event(
                    EventType.AI_RESPONSE_READY,
                    {
                        "query": query,
                        "response": response,
                        "org": context["org_name"]
                    },
                    org_id
                ))

            else:
                # Keep alive
                await manager.send_to_user(websocket, {
                    "type": "PONG",
                    "data": {"message": "alive"}
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket, org_id)