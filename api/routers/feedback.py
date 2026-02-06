from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from api import deps
from models.ml import PredictionFeedback
from models.user import User, Role
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class FeedbackCreate(BaseModel):
    prediction_id: UUID
    is_correct: bool
    actual_rul: float = None
    comment: str = None

@router.post("/feedback", response_model=FeedbackCreate) # Simple response for now
def submit_feedback(
    *,
    db: Session = Depends(deps.get_db),
    feedback_in: FeedbackCreate,
    current_user: User = Depends(deps.require_role([Role.ADMIN, Role.ENGINEER])),
) -> Any:
    # Check if prediction exists? (Skipped for performance unless strictly required, we trust ID or use service layer)
    # Ideally checking 'Prediction' hypertable by ID
    
    feedback = PredictionFeedback(
        prediction_id=feedback_in.prediction_id,
        is_correct=feedback_in.is_correct,
        actual_rul=feedback_in.actual_rul,
        comment=feedback_in.comment,
        org_id=current_user.org_id
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback_in
