from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.invitation import Invitation
from app.models.user import User
from app import schemas
from app.services.auth import get_current_user, require_admin, hash_password
from datetime import datetime, timedelta
import secrets

router = APIRouter(prefix="/invitations", tags=["Invitations"])

# 🔒 Admin only — send invite
@router.post("/", response_model=schemas.InviteResponse)
def send_invite(
    data: schemas.InviteCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Check if invite already sent
    existing_invite = db.query(Invitation).filter(
        Invitation.email == data.email,
        Invitation.organization_id == current_user["org_id"],
        Invitation.accepted == False
    ).first()
    if existing_invite:
        raise HTTPException(status_code=400, detail="Invite already sent to this email")

    # Create invite
    invite = Invitation(
        email=data.email,
        organization_id=current_user["org_id"],
        token=secrets.token_urlsafe(32),
        role=data.role,
        expires_at=datetime.now() + timedelta(days=7)
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return invite

# 🔒 Admin only — list all invites for my org
@router.get("/", response_model=list[schemas.InviteResponse])
def list_invites(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    return db.query(Invitation).filter(
        Invitation.organization_id == current_user["org_id"]
    ).all()

# Public — accept invite
@router.post("/accept", response_model=schemas.UserResponse)
def accept_invite(
    data: schemas.AcceptInvite,
    db: Session = Depends(get_db)
):
    # Find invite by token
    invite = db.query(Invitation).filter(
        Invitation.token == data.token
    ).first()

    if not invite:
        raise HTTPException(status_code=404, detail="Invalid invite token")

    if invite.accepted:
        raise HTTPException(status_code=400, detail="Invite already used")

    if datetime.now() > invite.expires_at:
        raise HTTPException(status_code=400, detail="Invite has expired")

    # Check email already registered
    existing = db.query(User).filter(User.email == invite.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user and join organization
    new_user = User(
        name=data.name,
        email=invite.email,
        password=hash_password(data.password),
        role=invite.role,
        organization_id=invite.organization_id
    )
    db.add(new_user)

    # Mark invite as accepted
    invite.accepted = True
    db.commit()
    db.refresh(new_user)
    return new_user

# 🔒 Admin only — cancel/delete invite
@router.delete("/{invite_id}")
def cancel_invite(
    invite_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    invite = db.query(Invitation).filter(
        Invitation.id == invite_id,
        Invitation.organization_id == current_user["org_id"]
    ).first()

    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")

    db.delete(invite)
    db.commit()
    return {"message": "Invite cancelled"}