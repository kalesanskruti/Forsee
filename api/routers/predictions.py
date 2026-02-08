from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api import deps
from models.ml import Asset, Prediction
from models.user import User, Organization, Role
from models.platform import AuditLog, Alert
from ml.inference import engine
from schemas.prediction import PredictionRequest, PredictionResponse
from services.data_quality import data_quality_service
from core.ratelimit import limiter
from starlette.requests import Request
from datetime import datetime
import json

router = APIRouter()

@router.post("/", response_model=PredictionResponse)
@limiter.limit("60/minute") # Example: 60 req/min per IP
def predict(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    pred_in: PredictionRequest,
    current_user: User = Depends(deps.require_role([Role.ADMIN, Role.ENGINEER])),
) -> Any:
    # 0. Data Quality Check
    errors = data_quality_service.validate_input(pred_in.data)
    if errors:
        raise HTTPException(status_code=400, detail={"message": "Data Quality check failed", "errors": errors})

    # 1. Validate Asset
    asset = db.query(Asset).filter(Asset.id == pred_in.asset_id, Asset.org_id == current_user.org_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # 2. Resolve Model
    model = engine.get_active_model(db, current_user.org_id, asset.type, pred_in.model_type)
    if not model:
        raise HTTPException(status_code=404, detail="No active model found for this asset type")

    # 3. Predict
    result = engine.predict(model.file_path, pred_in.data)
    
    # 4. Save Prediction
    prediction = Prediction(
        asset_id=asset.id,
        model_id=model.id,
        result=result,
        org_id=current_user.org_id
    )
    db.add(prediction)
    
    # Check thresholds (assuming result has 'risk_score')
    risk = result.get("risk_score", 0)
    
    # Get Org Config
    org = db.query(Organization).filter(Organization.id == current_user.org_id).first()
    warning_thresh = float(org.warning_threshold) if org.warning_threshold else 0.5
    critical_thresh = float(org.critical_threshold) if org.critical_threshold else 0.8
    
    if risk > warning_thresh:
        severity = "CRITICAL" if risk > critical_thresh else "WARNING"
        alert = Alert(
            asset_id=asset.id,
            risk_score=risk,
            message=f"High risk detected: {risk}",
            severity=severity,
            org_id=current_user.org_id
        )
        db.add(alert)
        
    # 5. Audit Log (using generic log or specific)
    audit = AuditLog(
        action="PREDICTION",
        details={"asset_id": str(asset.id), "model_id": str(model.id), "risk": risk},
        timestamp=datetime.utcnow(),
        user_id=current_user.id,
        org_id=current_user.org_id
    )
    db.add(audit)
    
    db.commit()
    
    return {"prediction": result, "model_id": model.id}
