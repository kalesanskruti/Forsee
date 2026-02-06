from sqlalchemy import Column, String, Float, Boolean, ForeignKey, Enum as SqlEnum, JSON, DateTime, func, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum
from db.base_class import Base, AuditMixin, SoftDeleteMixin, TenantMixin


class InputSchema(Base, AuditMixin, SoftDeleteMixin):
    __tablename__ = "input_schema"
    
    name = Column(String, nullable=False)
    system_type = Column(String, nullable=False) # e.g. "Wind Turbine", "Motor"
    schema_definition = Column(JSON, nullable=False) # { "sensor_1": "float", ... }
    active = Column(Boolean, default=True)

class Asset(Base, AuditMixin, SoftDeleteMixin, TenantMixin):
    __tablename__ = "asset"

    name = Column(String, nullable=False)
    type = Column(String, nullable=False) # e.g. Engine, Battery
    location = Column(String)
    status = Column(String) # OPERATIONAL, MAINTENANCE
    
    assigned_model_id = Column(UUID(as_uuid=True), ForeignKey("ml_model.id"), nullable=True)
    input_schema_id = Column(UUID(as_uuid=True), ForeignKey("input_schema.id"), nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="assets")

class Dataset(Base, AuditMixin, SoftDeleteMixin):
    __tablename__ = "dataset"

    name = Column(String, nullable=False)
    domain = Column(String) # Energy, Manufacturing
    industry = Column(String)
    data_type = Column(String) # tabular, timeseries, audio
    task_type = Column(String) # RUL, CLASSIFICATION, CLUSTERING
    source_type = Column(String, default="local") # local, remote
    source_path = Column(String, nullable=False)
    schema_json = Column(JSON, nullable=True)
    sample_count = Column(Integer, nullable=True)
    feature_list = Column(JSON, nullable=True)
    label_field = Column(String, nullable=True)
    dataset_version = Column(Integer, default=1)
    hash_checksum = Column(String, nullable=True)
    
    active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"), nullable=True)
    
    # Metadata for templates
    temporal = Column(Boolean, default=False)
    sampling_rate = Column(Float, nullable=True)
    recommended_window_size = Column(Integer, nullable=True)

class MLModel(Base, AuditMixin, SoftDeleteMixin, TenantMixin):
    __tablename__ = "ml_model"
    
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("dataset.id"), nullable=False)
    asset_type = Column(String, nullable=False)
    model_type = Column(String, nullable=False) # RUL, PRECURSOR, CLUSTERING
    algorithm = Column(String, nullable=True) # LSTM, XGBoost
    version = Column(String, nullable=False)
    
    accuracy = Column(Float)
    metrics = Column(JSON, nullable=True) # Detailed metrics
    
    file_path = Column(String, nullable=False)
    active = Column(Boolean, default=False)
    deployment_stage = Column(String, default="shadow") # shadow, canary, active
    
    input_feature_list = Column(JSON, nullable=True)
    window_size = Column(Integer, nullable=True)
    normalization_params = Column(JSON, nullable=True)
    
    checksum = Column(String, nullable=True)
    training_job_id = Column(UUID(as_uuid=True), ForeignKey("training_job.id"), nullable=True)

    organization = relationship("Organization", back_populates="models")
    # training_job relationship defined later

class MaintenanceEvent(Base, TenantMixin):
    __tablename__ = "maintenance_event"
    
    asset_id = Column(UUID(as_uuid=True), ForeignKey("asset.id"), nullable=False)
    action_taken = Column(String, nullable=False)
    actual_failure_time = Column(DateTime, nullable=True)
    prediction_feedback = Column(String, nullable=True) # correct, incorrect
    notes = Column(String, nullable=True)
    event_date = Column(DateTime, default=func.now())

class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class TrainingJob(Base, AuditMixin, TenantMixin):
    __tablename__ = "training_job"
    
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("dataset.id"), nullable=False)
    model_type = Column(String, nullable=False)
    status = Column(SqlEnum(JobStatus), default=JobStatus.PENDING)
    error_message = Column(String, nullable=True)
    artifact_path = Column(String, nullable=True)

class Prediction(Base, TenantMixin):
    __tablename__ = "prediction"
    
    asset_id = Column(UUID(as_uuid=True), ForeignKey("asset.id"), nullable=False)
    model_id = Column(UUID(as_uuid=True), ForeignKey("ml_model.id"), nullable=False)
    result = Column(JSON, nullable=False)
    # TimescaleDB requires the time column to NOT be indexed by default PK or strictly unique constraints that don't include it. 
    timestamp = Column(DateTime, default=func.now(), nullable=False)

class PredictionFeedback(Base, TenantMixin):
    __tablename__ = "prediction_feedback"
    
    # TimescaleDB limitation: No direct FKs to Hypertables (usually). 
    # We store valid UUID but remove strict DB constraint for simplicity here.
    prediction_id = Column(UUID(as_uuid=True), nullable=False, index=True) 

    is_correct = Column(Boolean, nullable=False)
    actual_rul = Column(Float, nullable=True)
    comment = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
class ModelMetric(Base, TenantMixin):
    __tablename__ = "model_metric"
    
    model_id = Column(UUID(as_uuid=True), ForeignKey("ml_model.id"), nullable=False)
    metric_name = Column(String, nullable=False) # e.g. "prediction_drift", "accuracy_last_7d"
    metric_value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=func.now())
