from sqlalchemy import Column, String, Boolean, ForeignKey, Enum as SqlEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from db.base_class import Base, AuditMixin, SoftDeleteMixin

class Role(str, enum.Enum):
    ADMIN = "ADMIN"
    ENGINEER = "ENGINEER"
    VIEWER = "VIEWER"

class Organization(Base, AuditMixin, SoftDeleteMixin):
    __tablename__ = "organization"
    
    name = Column(String, nullable=False)
    subscription_plan_id = Column(UUID(as_uuid=True), ForeignKey("plan.id"), nullable=True) # Billing scaffold
    
    # Config
    warning_threshold = Column(String, nullable=True) # JSON or simple value? Prompt says "Configuration... warning_threshold"
    critical_threshold = Column(String, nullable=True) 

    users = relationship("User", back_populates="organization")
    assets = relationship("Asset", back_populates="organization")
    models = relationship("MLModel", back_populates="organization")

class User(Base, AuditMixin, SoftDeleteMixin):
    __tablename__ = "user"

    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, index=True)
    is_active = Column(Boolean(), default=True)
    
    role = Column(SqlEnum(Role), default=Role.VIEWER, nullable=False)
    
    org_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"), nullable=False)
    organization = relationship("Organization", back_populates="users")

class ApiKey(Base, AuditMixin, SoftDeleteMixin):
    __tablename__ = "apikey"
    
    key_hash = Column(String, index=True, nullable=False)
    key_prefix = Column(String, index=True, nullable=False) # Store first few chars for identification
    name = Column(String, nullable=True)
    scopes = Column(String, nullable=False) # Comma separated list of scopes e.g., "predict,train"
    expires_at = Column(String, nullable=True) # Timestamp
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"), nullable=False)

    user = relationship("User")
    organization = relationship("Organization")
