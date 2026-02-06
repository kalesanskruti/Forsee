from sqlalchemy import Column, String, Float, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from db.base_class import Base, AuditMixin, SoftDeleteMixin, TenantMixin

class Plan(Base, AuditMixin):
    __tablename__ = "plan"
    
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    max_users = Column(Integer)
    max_models = Column(Integer)

class Alert(Base, AuditMixin, TenantMixin):
    __tablename__ = "alert"
    
    asset_id = Column(UUID(as_uuid=True), ForeignKey("asset.id"), nullable=False)
    risk_score = Column(Float, nullable=False)
    message = Column(String, nullable=False)
    severity = Column(String, nullable=False) # WARNING, CRITICAL
    
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    
class AuditLog(Base):
    __tablename__ = "audit_log"
    
    action = Column(String, nullable=False) # Login, Prediction, etc.
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, nullable=False)
    
    user_id = Column(UUID(as_uuid=True), nullable=True) # ID of user who performed action
    org_id = Column(UUID(as_uuid=True), nullable=True) 
    
    # Not using standard mixins because audit logs are immutable and shouldn't be soft deleted usually
