from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List, Optional
from uuid import UUID
import json
import hashlib
from datetime import datetime, timedelta

from models.intelligence import (
    DecisionRecord, AutonomyLevel, FailureMode, AssetDependency, 
    CostModel, TechnicalResource, SparePart
)
from models.ml import Asset, MLModel, MaintenanceEvent
from models.user import User

class IntelligenceService:
    @staticmethod
    def create_decision_record(
        db: Session,
        asset_id: UUID,
        model_id: UUID,
        risk_score: float,
        recommendation: str,
        urgency: str,
        confidence: float,
        drift_status: str,
        snapshot: Dict[str, Any],
        explainability: Dict[str, Any]
    ) -> DecisionRecord:
        """
        1. DECISION LEDGER
        Creates an immutable decision record.
        """
        # Calculate Hash Chain (Simple implementation)
        last_record = db.query(DecisionRecord).filter(DecisionRecord.asset_id == asset_id).order_by(DecisionRecord.timestamp.desc()).first()
        prev_hash = last_record.hash_chain if last_record and last_record.hash_chain else "GENESIS"
        
        # Payload to hash
        payload = f"{asset_id}{model_id}{risk_score}{recommendation}{prev_hash}{datetime.utcnow().isoformat()}"
        curr_hash = hashlib.sha256(payload.encode()).hexdigest()
        
        record = DecisionRecord(
            asset_id=asset_id,
            model_id=model_id,
            asset_state_snapshot=snapshot,
            risk_score=risk_score,
            recommended_action=recommendation,
            urgency_level=urgency,
            confidence_score=confidence,
            explainability_payload=explainability,
            data_drift_status=drift_status,
            hash_chain=curr_hash
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def check_autonomy(
        db: Session,
        asset: Asset,
        confidence: float,
        drift_status: str
    ) -> Dict[str, Any]:
        """
        2. HUMAN-AI AUTONOMY CONTROL
        Decides if action can be taken automatically.
        """
        policy = asset.autonomy_level
        
        # Hard limits
        if drift_status == "DRIFT_DETECTED":
            return {"allowed": False, "reason": "Data Drift Detected - Human Approval Required", "level": policy}
            
        if policy == AutonomyLevel.ADVISORY:
             return {"allowed": False, "reason": "Asset is in Advisory Mode", "level": policy}
             
        if policy == AutonomyLevel.APPROVAL_REQUIRED:
            return {"allowed": False, "reason": "Policy Requires Approval", "level": policy}
            
        if policy == AutonomyLevel.FULL_AUTONOMY:
            if confidence > 0.85: # Threshold
                return {"allowed": True, "reason": "High Confidence - Autonomy Granted", "level": policy}
            else:
                return {"allowed": False, "reason": "Low Confidence for Autonomy", "level": policy}
                
        return {"allowed": False, "reason": "Unknown Policy", "level": policy}

    @staticmethod
    def calculate_failure_economics(
        db: Session,
        asset: Asset,
        failure_mode_name: str
    ) -> Dict[str, float]:
        """
        3. FAILURE ECONOMICS ENGINE
        6. CROSS-ASSET DEPENDENCY GRAPH (Cost Propagation)
        """
        # Find Cost Model
        cost_config = db.query(CostModel).filter(CostModel.asset_id == asset.id).first()
        if not cost_config:
            # Fallback to defaults (using a mock object or org default)
            cost_config = CostModel(labor_rate_hourly=50, downtime_cost_hourly=500)
            
        # Find Failure Mode
        mode = db.query(FailureMode).filter(
            FailureMode.name == failure_mode_name, 
            FailureMode.asset_type == asset.type
        ).first()
        
        direct_cost = 0.0
        indirect_cost = 0.0
        
        if mode:
            direct_cost = mode.direct_cost_est
            indirect_cost = mode.avg_mttr_hours * cost_config.downtime_cost_hourly
        
        # 6. Propagation (Cross-Asset)
        downstream = db.query(AssetDependency).filter(AssetDependency.upstream_asset_id == asset.id).all()
        cascading_cost = 0.0
        
        for dep in downstream:
            # Simplified: Add 20% of parent downtime cost * weight
            cascading_cost += (indirect_cost * 0.2 * dep.impact_weight)
            
        total_risk = direct_cost + indirect_cost + cascading_cost
        
        return {
            "direct_cost": direct_cost,
            "indirect_cost": indirect_cost,
            "cascading_risk": cascading_cost,
            "total_failure_cost": total_risk
        }

    @staticmethod
    def check_feasibility(
        db: Session,
        action_required: str
    ) -> Dict[str, Any]:
        """
        5. EXECUTION FEASIBILITY ENGINE
        """
        # Heuristic mapping of action -> skills/parts
        # In real system, this is a table.
        required_skill = "General"
        if "Replace" in action_required: required_skill = "Mechanical"
        if "Calibrate" in action_required: required_skill = "Calibration"
        
        # Check Techs
        techs = db.query(TechnicalResource).all()
        available_techs = [t for t in techs if t.is_available and required_skill in (t.skills or [])]
        
        score = 100
        issues = []
        
        if not available_techs:
            score -= 50
            issues.append(f"No technicians with {required_skill} skill available.")
            
        # Check Parts (Mock)
        # If we had parts linked to action
        
        return {
            "feasibility_score": score,
            "is_feasible": score > 0,
            "issues": issues
        }

    @staticmethod
    def process_outcome_feedback(
        db: Session,
        asset_id: UUID,
        action_taken: str,
        was_successful: bool,
        notes: str
    ):
        """
        4. OUTCOME FEEDBACK & LEARNING LOOP
        """
        # Find the last decision for this asset
        last_decision = db.query(DecisionRecord).filter(
            DecisionRecord.asset_id == asset_id
        ).order_by(DecisionRecord.timestamp.desc()).first()
        
        if last_decision:
            # Update Outcome
            last_decision.outcome = {
                "action_taken": action_taken,
                "success": was_successful,
                "notes": notes,
                "processed_at": datetime.utcnow().isoformat()
            }
            db.commit()
            
            # TRIGGER LEARNING (Step 9 & 10)
            # If AI was wrong (success=False), we flag the model
            if not was_successful:
                print(f"Outcome Feedback: AI Mismatch for Asset {asset_id}. Triggering review.")
                # Logic to lower model confidence or trigger retraining would go here.
