from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), unique=True, nullable=False)
    plan = Column(String, default="free")  # free, pro, enterprise
    status = Column(String, default="active")  # ✅ fixed "activate" → "active"
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)  # ✅ fixed create_at → created_at
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # ✅ fixed update_at → updated_at

    organization = relationship("Organization", back_populates="subscription")