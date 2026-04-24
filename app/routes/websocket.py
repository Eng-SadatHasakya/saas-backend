from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.websocket.manager import manager
from app.websocket.events import create_event, EventType
from jose import jwt, JWTError
from dotenv import load_dotenv
import os

load_dotenv(
    dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
    override=True
)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

router = APIRouter(tags=["WebSocket"])

def get_user_from_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "email": payload.get("sub"),
            "role": payload.get("role"),
            "org_id": payload.get("org_id")
        }
    except JWTError:
        return None

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...)
):
    # Authenticate via token
    user = get_user_from_token(token)
    if not user:
        await websocket.close(code=4001)
        return

    org_id = user["org_id"]

    # Connect to org group
    await manager.connect(websocket, org_id)

    # Send welcome message
    await manager.send_to_user(websocket, create_event(
        EventType.NOTIFICATION,
        {"message": f"Connected to real-time updates for your organization"},
        org_id
    ))

    try:
        while True:
            # Keep connection alive and listen for messages
            data = await websocket.receive_text()
            # Echo back for now
            await manager.send_to_user(websocket, {
                "type": "PONG",
                "data": {"message": "Connection alive"}
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket, org_id)