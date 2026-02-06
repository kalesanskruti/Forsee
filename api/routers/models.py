from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from api import deps
from models.ml import MLModel
from models.user import User, Role
from schemas.ml import MLModel as MLModelSchema, MLModelCreate

router = APIRouter()

@router.get("/", response_model=List[MLModelSchema])
def read_models(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_role([Role.ADMIN, Role.ENGINEER, Role.VIEWER])),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    models = db.query(MLModel).filter(MLModel.org_id == current_user.org_id).offset(skip).limit(limit).all()
    return models

@router.post("/register", response_model=MLModelSchema)
def register_model(
    *,
    db: Session = Depends(deps.get_db),
    model_in: MLModelCreate,
    current_user: User = Depends(deps.require_admin),
) -> Any:
    model = MLModel(
        **model_in.dict(),
        org_id=current_user.org_id,
        active=False # Inactive by default
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    return model

@router.post("/{id}/activate", response_model=MLModelSchema)
def activate_model(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
    current_user: User = Depends(deps.require_role([Role.ADMIN, Role.ENGINEER])),
) -> Any:
    model = db.query(MLModel).filter(MLModel.id == id, MLModel.org_id == current_user.org_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Deactivate others of same type/asset_type for this org
    # Implementation detail: One active model per (org, asset_type, model_type)
    others = db.query(MLModel).filter(
        MLModel.org_id == current_user.org_id,
        MLModel.asset_type == model.asset_type,
        MLModel.model_type == model.model_type,
        MLModel.active == True
    ).all()
    
    for other in others:
        other.active = False
        db.add(other)
    
    model.active = True
    db.add(model)
    db.commit()
    db.refresh(model)
    return model
