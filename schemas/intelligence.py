from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

# --- Decision Ledger ---
class DecisionRecordBase(BaseModel):
    asset_id: uuid.UUID
    model_id: uuid.UUID
    risk_score: float
    recommended_action: str
    urgency_level: str
    confidence_score: float
    explainability_payload: Optional[Dict[str, Any]] = None

class DecisionRecordCreate(DecisionRecordBase):
    asset_state_snapshot: Dict[str, Any]
    uncertainty_score: float
    alternative_actions: Optional[List[Dict[str, Any]]] = None
    data_drift_status: str

class DecisionRecordOut(DecisionRecordBase):
    id: uuid.UUID
    timestamp: datetime
    human_action: Optional[str]
    outcome: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True

# --- Economics ---
class FailureModeCreate(BaseModel):
    name: str
    asset_type: str
    direct_cost_est: float
    indirect_cost_hourly: float
    avg_mttr_hours: float

class CostRiskAnalysis(BaseModel):
    asset_id: uuid.UUID
    failure_mode: str
    probability_7d: float
    estimated_cost: float
    roi_of_action: float

# --- Autonomy ---
class AutonomyUpdate(BaseModel):
    autonomy_level: str # ADVISORY, FULL_AUTONOMY
    criticality_score: int

# --- Governance ---
class ModelGovernanceUpdate(BaseModel):
    status: str # APPROVED, REJECTED
    approved_by: uuid.UUID
    comment: Optional[str]
