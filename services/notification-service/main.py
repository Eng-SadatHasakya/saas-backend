from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import httpx
import os
from dotenv import load_dotenv

load_dotenv(
    dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
    override=True
)

app = FastAPI(
    title="Notification Service",
    description="Standalone notification microservice",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for demo (use Redis in production)
notifications_store = {}

class NotificationCreate(BaseModel):
    org_id: int
    message: str
    event_type: str

class NotificationResponse(BaseModel):
    id: int
    org_id: int
    message: str
    event_type: str
    is_read: bool
    created_at: str

@app.get("/health")
def health():
    return {"status": "healthy", "service": "notification-service"}

@app.post("/notifications", response_model=NotificationResponse)
def create_notification(data: NotificationCreate):
    """Create notification — called by other services"""
    org_id = data.org_id
    if org_id not in notifications_store:
        notifications_store[org_id] = []

    notification = {
        "id": len(notifications_store[org_id]) + 1,
        "org_id": org_id,
        "message": data.message,
        "event_type": data.event_type,
        "is_read": False,
        "created_at": datetime.now().isoformat()
    }
    notifications_store[org_id].append(notification)
    return notification

@app.get("/notifications/{org_id}", response_model=List[NotificationResponse])
def get_notifications(org_id: int):
    """Get notifications for org"""
    return notifications_store.get(org_id, [])

@app.put("/notifications/{org_id}/read-all")
def mark_all_read(org_id: int):
    """Mark all notifications as read"""
    if org_id in notifications_store:
        for n in notifications_store[org_id]:
            n["is_read"] = True
    return {"message": "All notifications marked as read"}

@app.get("/notifications/{org_id}/unread-count")
def unread_count(org_id: int):
    """Get unread count"""
    notifications = notifications_store.get(org_id, [])
    count = sum(1 for n in notifications if not n["is_read"])
    return {"count": count}