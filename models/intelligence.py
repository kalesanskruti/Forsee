from sqlalchemy import Column, String, Float, Boolean, ForeignKey, Enum as SqlEnum, JSON, DateTime, func, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum
from db.base_class import Base, AuditMixin, SoftDeleteMixin, TenantMixin

class AutonomyLevel(str, enum.Enum):
    ADVISORY = "ADVISORY" # Suggestion only
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED" # Needs click to proceed
    AUTONOMOUS_CONSTRAINED = "AUTONOMOUS_CONSTRAINED" # Action strictly within bounds
    FULL_AUTONOMY = "FULL_AUTONOMY" # Action taken automatically if confidence high

class DecisionRecord(Base, TenantMixin):
    """
    Immutable ledger of AI recommendations and decisions using cryptographic chaining if needed in future.
    """
    __tablename__ = "decision_record"
    
    # Core linkage
    asset_id = Column(UUID(as_uuid=True), ForeignKey("asset.id"), nullable=False)
    model_id = Column(UUID(as_uuid=True), ForeignKey("ml_model.id"), nullable=False)
    
    # State Snapshot - What did the asset look like?
    asset_state_snapshot = Column(JSON, nullable=False) # Features + Stats
    risk_score = Column(Float, nullable=False)
    uncertainty_score = Column(Float, nullable=True) # Epistemic uncertainty
    
    # Recommendation
    recommended_action = Column(String, nullable=False)
    urgency_level = Column(String, nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    confidence_score = Column(Float, nullable=False)
    
    # Explainability
    explainability_payload = Column(JSON, nullable=True) # SHAP values, top contributors
    alternative_actions = Column(JSON, nullable=True) # List of rejected options
    
    # Human Interaction
    human_action = Column(String, nullable=True) # ACCEPTED, OVERRIDDEN, DELAYED
    human_comment = Column(String, nullable=True)
    performed_by_user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    
    # Outcome (Feedback Loop)
    outcome = Column(JSON, nullable=True) # Filled post-action: { "cost_saved": 1000, "was_correct": true }
    
    # Metadata
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    hash_chain = Column(String, nullable=True) # For audit integrity
    
    # Drift Status at moment of decision
    data_drift_status = Column(String, nullable=True) # NORMAL, DRIFT_DETECTED

class FailureMode(Base, TenantMixin):
    """
    Defining how things fail and what it costs.
    """
    __tablename__ = "failure_mode"
    
    name = Column(String, nullable=False)
    description = Column(String)
    
    # Economic Impact
    direct_cost_est = Column(Float, default=0.0) # Parts/Labor
    indirect_cost_hourly = Column(Float, default=0.0) # Downtime cost
    safety_penalty_cost = Column(Float, default=0.0)
    
    avg_mttr_hours = Column(Float) # Mean Time To Repair
    
    asset_type = Column(String, nullable=False) # e.g. "Turbofan Engine"

class AssetDependency(Base, TenantMixin):
    """
    Directed graph of asset dependencies for cross-asset reasoning.
    """
    __tablename__ = "asset_dependency"
    
    upstream_asset_id = Column(UUID(as_uuid=True), ForeignKey("asset.id"), nullable=False)
    downstream_asset_id = Column(UUID(as_uuid=True), ForeignKey("asset.id"), nullable=False)
    dependency_type = Column(String, default="critical") # critical, redundant, enhancing
    
    impact_weight = Column(Float, default=1.0) # Multiplier for cost propagation

class CostModel(Base, TenantMixin):
    """
    Dynamic cost configurations per asset or org.
    """
    __tablename__ = "cost_model"
    
    asset_id = Column(UUID(as_uuid=True), ForeignKey("asset.id"), nullable=True) # If null, applies to Org defaults
    currency = Column(String, default="USD")
    
    labor_rate_hourly = Column(Float, default=50.0)
    downtime_cost_hourly = Column(Float, default=500.0)
    
    # JSON for complex logic (e.g., penalty curves)
    penalty_logic = Column(JSON, nullable=True)

# --- Feasibility Engine Models ---
class TechnicalResource(Base, TenantMixin):
    """Technicians and their skills."""
    __tablename__ = "technical_resource"
    name = Column(String, nullable=False)
    skills = Column(JSON, nullable=False) # ["electrical", "hydraulic"]
    is_available = Column(Boolean, default=True)

class SparePart(Base, TenantMixin):
    """Inventory for maintenance."""
    __tablename__ = "spare_part"
    name = Column(String, nullable=False)
    sku = Column(String, unique=True, nullable=False)
    quantity_on_hand = Column(Integer, default=0)
    cost_per_unit = Column(Float, default=0.0)
    lead_time_days = Column(Integer, default=1)
