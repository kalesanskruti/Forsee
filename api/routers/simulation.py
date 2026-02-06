from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from api import deps
from models.user import User, Role
from services.os_core import SimulationService, RecommendationEngine
from pydantic import BaseModel
from typing import Dict

router = APIRouter()
sim_service = SimulationService()

class SimulationRequest(BaseModel):
    model_id: UUID
    scenario: Dict[str, Any]

@router.post("/run", response_model=Dict[str, Any])
def run_simulation(
    *,
    sim_req: SimulationRequest,
    current_user: User = Depends(deps.require_role([Role.ADMIN, Role.ENGINEER])),
) -> Any:
    # Validate access to model/org
    return sim_service.run_simulation(sim_req.model_id, sim_req.scenario)
