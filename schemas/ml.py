from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from models.ml import JobStatus

class AssetBase(BaseModel):
    name: str
    type: str
    location: Optional[str] = None
    status: Optional[str] = "OPERATIONAL"

class AssetCreate(AssetBase):
    pass

class AssetUpdate(AssetBase):
    pass

class Asset(AssetBase):
    id: UUID
    org_id: UUID
    assigned_model_id: Optional[UUID] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class DatasetBase(BaseModel):
    name: str
    domain: Optional[str] = None
    data_type: Optional[str] = None
    task_type: Optional[str] = None
    path: str 
    is_public: bool = False

class DatasetCreate(DatasetBase):
    pass

class Dataset(DatasetBase):
    id: UUID
    active: bool = True
    org_id: Optional[UUID] = None # Optional for public datasets
    
    class Config:
        from_attributes = True

class MLModelBase(BaseModel):
    asset_type: str
    model_type: str
    version: str
    accuracy: float
    file_path: str
    dataset_id: UUID

class MLModelCreate(MLModelBase):
    pass

class MLModel(MLModelBase):
    id: UUID
    active: bool
    org_id: UUID
    checksum: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class TrainingJobBase(BaseModel):
    dataset_id: UUID
    model_type: str

class TrainingJob(TrainingJobBase):
    id: UUID
    status: JobStatus
    error_message: Optional[str] = None
    artifact_path: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
