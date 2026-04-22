from click import option
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Organization schemas
class OrganizationCreate(BaseModel):
    name: str

class OrganizationResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True

# User schemas
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    organization_name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    organization_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

# Token schemas
class RefreshTokenRequest(BaseModel):
    refresh_token: str

# Subscription schemas
class SubscriptionResponse(BaseModel):
    id: int
    organization_id: int
    plan: str
    status: str
    expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class SubscriptionUpdate(BaseModel):
    plan: str # free, pro, enterprise

# Invitation schemas
class InviteCreate(BaseModel):
    email: str
    role: str = "User" # default role is user

class InviteResponse(BaseModel):
    id: int
    email: str
    organization_id: int
    token: str
    role: str 
    accepted: bool
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class AcceptInvite(BaseModel):
    token: str
    name: str
    password: str

# API Key schemas
class APIKeyCreate(BaseModel):
    name: str
    expires_in_days: Optional[int] = None  # None means never expires

class APIKeyResponse(BaseModel):
    id: int
    name: str
    key: str
    organization_id: int
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True