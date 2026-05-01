from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.notification import Notification
from app.services.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/notifications", tags=["Notifications"])

class NotificationResponse(BaseModel):
    id: int
    message: str
    event_type: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

# 🔒 Get all notifications for my org
@router.get("/", response_model=list[NotificationResponse])
def get_notifications(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return db.query(Notification).filter(
        Notification.organization_id == current_user["org_id"]
    ).order_by(Notification.created_at.desc()).limit(50).all()

# 🔒 Mark all as read
@router.put("/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db.query(Notification).filter(
        Notification.organization_id == current_user["org_id"],
        Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    return {"message": "All notifications marked as read"}

# 🔒 Get unread count
@router.get("/unread-count")
def unread_count(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    count = db.query(Notification).filter(
        Notification.organization_id == current_user["org_id"],
        Notification.is_read == False
    ).count()
    return {"count": count}