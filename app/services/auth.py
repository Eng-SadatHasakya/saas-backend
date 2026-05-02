from app.core.security import (
    hash_password, verify_password,
    create_access_token, get_current_user,
    require_admin, oauth2_scheme
)
from app.core.config import settings
import secrets
from datetime import datetime

def create_refresh_token() -> str:
    return secrets.token_urlsafe(32)

def is_token_expired(expires_at: datetime) -> bool:
    return datetime.now() > expires_at