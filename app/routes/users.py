from app.services.event_service import emit_user_created, emit_user_deleted
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.organization import Organization
from app import schemas
from app.services.auth import (
    get_current_user, require_admin,
    hash_password
)
from app.services.tenant import (
    get_users_in_org, get_user_in_org,
    delete_user_in_org, get_org_or_404
)

router = APIRouter(prefix="/users", tags=["Users"])

# 🔒 Get all users in MY organization only
@router.get("/", response_model=list[schemas.UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    # ✅ Tenant isolation — only sees own org users
    return get_users_in_org(db, current_user["org_id"])

# 🔒 Get my own profile
@router.get("/me", response_model=schemas.UserResponse)
def get_me(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user = db.query(User).filter(User.email == current_user["email"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# 🔒 Get a specific user in MY organization
@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    # ✅ Tenant isolation — cannot access users from other orgs
    return get_user_in_org(db, user_id, current_user["org_id"])

# 🔒 Add a new member to MY organization
@router.post("/", response_model=schemas.UserResponse)
async def add_member(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        role="user",
        organization_id=current_user["org_id"]
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    await emit_user_created(current_user["org_id"], {
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
        "role": new_user.role
    })

    return new_user

    # ✅ Emit real-time event
    import asyncio
    asyncio.create_task(emit_user_created(current_user["org_id"], {
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
        "role": new_user.role
    }))

    return new_user

# 🔒 Delete a user from MY organization
@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    user = get_user_in_org(db, user_id, current_user["org_id"])
    db.delete(user)
    db.commit()
    await emit_user_deleted(current_user["org_id"], user_id)
    return {"message": "Deleted"}