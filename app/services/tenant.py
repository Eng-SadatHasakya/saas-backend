from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.organization import Organization

def get_org_or_404(db: Session, org_id: int):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

def get_users_in_org(db: Session, org_id: int):
    """Only return users belonging to the same organization"""
    return db.query(User).filter(User.organization_id == org_id).all()

def get_user_in_org(db: Session, user_id: int, org_id: int):
    """Get a specific user only if they belong to the same organization"""
    user = db.query(User).filter(
        user.id == user_id,
        user.organization_id == org_id
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found in your organization")
    return user

def delete_user_in_org(db: Session, user_id: int, org_id: int):
    user = get_user_in_org(db, user_id, org_id)
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}