from pydantic import BaseModel
from typing import Dict, Any
from uuid import UUID

class PredictionRequest(BaseModel):
    asset_id: UUID
    data: Dict[str, Any]
    model_type: str = "RUL" # Default

class PredictionResponse(BaseModel):
    prediction: Dict[str, Any]
    model_id: UUID
