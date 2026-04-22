from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.organization import Organization
from app.models.refresh_token import RefreshToken
from app import schemas
from app.services.auth import (
    hash_password, verify_password, create_access_token,
    create_refresh_token, is_token_expired, get_current_user
)
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create organization
    org = db.query(Organization).filter(
        Organization.name == user.organization_name
    ).first()

    if not org:
        org = Organization(name=user.organization_name)
        db.add(org)
        db.commit()
        db.refresh(org)

    # Create user as admin of the org
    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        role="admin",
        organization_id=org.id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # ✅ Auto-create free subscription for new org
    from app.routes.subscriptions import create_default_subscription
    create_default_subscription(db, org.id)

    return new_user

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.email == form_data.username).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if not verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # ✅ Include org_id in token
    access_token = create_access_token(data={
        "sub": db_user.email,
        "role": db_user.role,
        "org_id": db_user.organization_id
    })
    refresh_token = create_refresh_token()

    # Save refresh token
    expires = datetime.now() + timedelta(days=7)
    db_token = RefreshToken(
        token=refresh_token,
        user_email=db_user.email,
        expires_at=expires
    )
    db.add(db_token)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh")
def refresh_token(
    request: schemas.RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == request.refresh_token
    ).first()

    if not db_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if is_token_expired(db_token.expires_at):
        db.delete(db_token)
        db.commit()
        raise HTTPException(status_code=401, detail="Refresh token expired")

    new_access_token = create_access_token(data={"sub": db_token.user_email})
    return {"access_token": new_access_token, "token_type": "bearer"}

@router.post("/logout")
def logout(
    request: schemas.RefreshTokenRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == request.refresh_token
    ).first()
    if db_token:
        db.delete(db_token)
        db.commit()
    return {"message": "Logged out successfully"}