from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    key = Column(String, unique=True, nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime, nullable=True)

    organization = relationship("Organization", back_populates="api_keys")  