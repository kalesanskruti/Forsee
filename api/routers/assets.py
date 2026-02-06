from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from api import deps
from models.ml import Asset
from models.user import User, Role
from schemas.ml import Asset as AssetSchema, AssetCreate, AssetUpdate

router = APIRouter()

@router.get("/", response_model=List[AssetSchema])
def read_assets(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_role([Role.ADMIN, Role.ENGINEER, Role.VIEWER])),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    assets = db.query(Asset).filter(Asset.org_id == current_user.org_id).offset(skip).limit(limit).all()
    return assets

@router.post("/", response_model=AssetSchema)
def create_asset(
    *,
    db: Session = Depends(deps.get_db),
    asset_in: AssetCreate,
    current_user: User = Depends(deps.require_role([Role.ADMIN, Role.ENGINEER])),
) -> Any:
    asset = Asset(
        **asset_in.dict(),
        org_id=current_user.org_id
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset

@router.put("/{id}", response_model=AssetSchema)
def update_asset(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
    asset_in: AssetUpdate,
    current_user: User = Depends(deps.require_role([Role.ADMIN, Role.ENGINEER])),
) -> Any:
    asset = db.query(Asset).filter(Asset.id == id, Asset.org_id == current_user.org_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    update_data = asset_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(asset, field, value)
    
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset

@router.delete("/{id}", response_model=AssetSchema)
def delete_asset(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
    current_user: User = Depends(deps.require_admin),
) -> Any:
    asset = db.query(Asset).filter(Asset.id == id, Asset.org_id == current_user.org_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Soft delete provided by mixin? But I need to set deleted_at.
    # The SoftDeleteMixin provides the column 'deleted_at'.
    # I should set it to datetime.now()
    from datetime import datetime
    asset.deleted_at = datetime.utcnow()
    db.add(asset)
    db.commit()
    return asset
