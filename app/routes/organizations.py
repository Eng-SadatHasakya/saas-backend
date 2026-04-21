from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.organization import Organization
from app import schemas
from app.services.auth import get_current_user, require_admin
from app.services.tenant import get_org_or_404

router = APIRouter(prefix="/organizations", tags=["Organizations"])

#Get MY organization details
@router.get("/me", response_model=schemas.OrganizationResponse)
def get_my_org(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    #Only returns the user's organization
    return get_org_or_404(db, current_user["org_id"])

#Update MY organization name
@router.put("/me", response_model=schemas.OrganizationResponse)
def update_my_org(
    org_data: schemas.OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    org = get_org_or_404(db, current_user["org_id"])
    org.name = org_data.name
    db.commit()
    db.refresh(org)
    return org