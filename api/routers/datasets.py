from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, or_
from uuid import UUID

from api import deps
from models.ml import Dataset
from models.user import User, Role
from schemas.ml import Dataset as DatasetSchema, DatasetCreate

router = APIRouter()

@router.get("/", response_model=List[DatasetSchema])
def read_datasets(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_role([Role.ADMIN, Role.ENGINEER, Role.VIEWER])),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    datasets = db.query(Dataset).filter(
        or_(Dataset.org_id == current_user.org_id, Dataset.is_public == True)
    ).offset(skip).limit(limit).all()
    return datasets

@router.post("/register", response_model=DatasetSchema)
def register_dataset(
    *,
    db: Session = Depends(deps.get_db),
    dataset_in: DatasetCreate,
    current_user: User = Depends(deps.require_admin),
) -> Any:
    dataset = Dataset(
        **dataset_in.dict(),
        org_id=current_user.org_id,
        is_public=False # New registers are private by default unless specifically handled
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset

@router.post("/{id}/activate", response_model=DatasetSchema)
def activate_dataset(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
    current_user: User = Depends(deps.require_admin),
) -> Any:
    dataset = db.query(Dataset).filter(
        Dataset.id == id, 
        or_(Dataset.org_id == current_user.org_id, Dataset.is_public == True)
    ).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Only allow modifying if it belongs to org, or if user is system admin?
    # Assuming Org Admin can only modify Org datasets. Public ones are read-only for them?
    if dataset.is_public:
        raise HTTPException(status_code=403, detail="Cannot modify public datasets")
    
    dataset.active = True
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset
