from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.database import Base
from datetime import datetime

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, nullable=False)
    user_email = Column(String, ForeignKey("users.email"))
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)