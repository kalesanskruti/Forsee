from typing import Any
from sqlalchemy.orm import as_declarative, declared_attr
from sqlalchemy import Column, Integer, DateTime, String, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid

@as_declarative()
class Base:
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    __allow_unmapped__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)


class SoftDeleteMixin:
    deleted_at = Column(DateTime, nullable=True)

class AuditMixin:
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=True) # User ID

class TenantMixin:
    @declared_attr
    def org_id(cls):
        return Column(UUID(as_uuid=True), ForeignKey("organization.id"), nullable=True, index=True)


