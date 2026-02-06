from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Any
from uuid import UUID

from api import deps
from services.intelligence import IntelligenceService
from schemas.intelligence import DecisionRecordCreate, DecisionRecordOut, CostRiskAnalysis
from models.ml import Asset

router = APIRouter()

@router.post("/decisions", response_model=DecisionRecordOut)
def record_decision(
    *,
    db: Session = Depends(deps.get_db),
    decision_in: DecisionRecordCreate
) -> Any:
    """
    1. DECISION LEDGER API
    Called by the AI Engine to log a decision immutably.
    Also validates Autonomy and Feasibility implicitly (or explicitly if we add checks).
    """
    # 1. Fetch Asset to check autonomy policy
    asset = db.query(Asset).filter(Asset.id == decision_in.asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # 2. Check Autonomy (SubSystem 2)
    autonomy_check = IntelligenceService.check_autonomy(
        db, asset, decision_in.confidence_score, decision_in.data_drift_status
    )
    
    # 3. Create Record
    record = IntelligenceService.create_decision_record(
        db=db,
        asset_id=decision_in.asset_id,
        model_id=decision_in.model_id,
        risk_score=decision_in.risk_score,
        recommendation=decision_in.recommended_action,
        urgency=decision_in.urgency_level,
        confidence=decision_in.confidence_score,
        drift_status=decision_in.data_drift_status,
        snapshot=decision_in.asset_state_snapshot,
        explainability=decision_in.explainability_payload
    )
    
    # 4. Attach Autonomy Result to alternative_actions or metadata for now? 
    # Or just return it. Extending response model on the fly for API convenience.
    # The requirement says "Audit of all autonomous actions".
    # We recorded the decision. If autonomy said "True", the system might AUTO EXECUTE.
    # That logic usually sits in a "ActionEngine" or "Orchestrator".
    
    return record

@router.get("/economics/{asset_id}/{failure_mode}", response_model=CostRiskAnalysis)
def analyze_risk(
    *,
    db: Session = Depends(deps.get_db),
    asset_id: UUID,
    failure_mode: str
) -> Any:
    """
    3. FAILURE ECONOMICS ENGINE API
    Returns the financial impact of a specific failure mode for an asset.
    """
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
        
    economics = IntelligenceService.calculate_failure_economics(db, asset, failure_mode)
    
    # Pack into response
    return {
        "asset_id": asset_id,
        "failure_mode": failure_mode,
        "probability_7d": 0.05, # Mock: meaningful value requires Predictive Model query
        "estimated_cost": economics["total_failure_cost"],
        "roi_of_action": economics["total_failure_cost"] * 0.9 # Heuristic: Prevention saves 90%
    }

@router.post("/feedback")
def submit_outcome(
    *,
    db: Session = Depends(deps.get_db),
    asset_id: UUID,
    action_taken: str,
    was_successful: bool,
    notes: str
) -> Any:
    """
    4. OUTCOME FEEDBACK LOOP API
    """
    IntelligenceService.process_outcome_feedback(
        db, asset_id, action_taken, was_successful, notes
    )
    return {"status": "recorded"}

@router.get("/feasibility/{action_required}")
def check_execution_feasibility(
    *,
    db: Session = Depends(deps.get_db),
    action_required: str
) -> Any:
    """
    5. FEASIBILITY ENGINE API
    """
    return IntelligenceService.check_feasibility(db, action_required)
