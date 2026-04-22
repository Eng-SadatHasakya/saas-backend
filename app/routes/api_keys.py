from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.api_key import APIKey
from app.models.organization import Organization
from app import schemas
from app.services.auth import get_current_user, require_admin
from datetime import datetime, timedelta
import secrets

router = APIRouter(prefix="/api-keys", tags=["API Keys"])

# API Key header scheme
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

# 🔒 Validate API key — used by external services
def get_org_from_api_key(
    api_key: str = Security(api_key_header),
    db: Session = Depends(get_db)
):
    if not api_key:
        raise HTTPException(status_code=401, detail="API key missing")

    db_key = db.query(APIKey).filter(
        APIKey.key == api_key,
        APIKey.is_active == True
    ).first()

    if not db_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    if db_key.expires_at and datetime.now() > db_key.expires_at:
        raise HTTPException(status_code=401, detail="API key expired")

    return db_key.organization_id

# 🔒 Admin only — create API key
@router.post("/", response_model=schemas.APIKeyResponse)
def create_api_key(
    data: schemas.APIKeyCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    expires_at = None
    if data.expires_in_days:
        expires_at = datetime.now() + timedelta(days=data.expires_in_days)

    new_key = APIKey(
        name=data.name,
        key=f"sk_{secrets.token_urlsafe(32)}",  # ✅ prefixed like real API keys
        organization_id=current_user["org_id"],
        expires_at=expires_at
    )
    db.add(new_key)
    db.commit()
    db.refresh(new_key)
    return new_key

# 🔒 Admin only — list all API keys for my org
@router.get("/", response_model=list[schemas.APIKeyResponse])
def list_api_keys(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    return db.query(APIKey).filter(
        APIKey.organization_id == current_user["org_id"]
    ).all()

# 🔒 Admin only — revoke API key
@router.delete("/{key_id}")
def revoke_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    db_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.organization_id == current_user["org_id"]
    ).first()

    if not db_key:
        raise HTTPException(status_code=404, detail="API key not found")

    db_key.is_active = False
    db.commit()
    return {"message": "API key revoked"}

# Public — test endpoint accessible via API key
@router.get("/verify")
def verify_api_key(
    org_id: int = Depends(get_org_from_api_key)
):
    return {
        "message": "API key is valid",
        "organization_id": org_id
    }