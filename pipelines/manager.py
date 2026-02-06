from sqlalchemy.orm import Session
from models.ml import TrainingJob, JobStatus, Dataset, MLModel
from uuid import UUID
import time
import pickle
import os

# Mock pipeline execution
def run_training_pipeline(job_id: UUID, db: Session):
    # This would typically be a Celery task
    job = db.query(TrainingJob).filter(TrainingJob.id == job_id).first()
    if not job:
        print(f"Job {job_id} not found")
        return
        
    try:
        print(f"Starting pipeline for Job {job_id}...")
        job.status = JobStatus.RUNNING
        db.commit()
        
        # Simulate work
        time.sleep(2) 
        
        # In real world: Load data, train, save artifact
        # We save a REAL dummy file to disk so the USER can see it
        
        models_dir = "datasets/models"
        os.makedirs(models_dir, exist_ok=True)
        
        # Fetch dataset to name the file
        dataset = db.query(Dataset).filter(Dataset.id == job.dataset_id).first()
        dataset_name = dataset.name if dataset else "unknown"
        # Sanitize name: replace non-alnum with _, strip leading/trailing _
        safe_name = "".join(c if c.isalnum() or c == '-' else '_' for c in dataset_name)
        while "__" in safe_name:
            safe_name = safe_name.replace("__", "_")
        safe_name = safe_name.strip('_')
        
        filename = f"{safe_name}_{job.model_type}.pkl"
        filepath = os.path.join(models_dir, filename).replace("\\", "/")
        
        # Create a dummy model artifact (dictionary for now)
        artifact = {
            "model_type": job.model_type,
            "job_id": str(job_id),
            "dataset": dataset_name,
            "trained_at": time.time(),
            "weights": "0.123,0.456,0.789" # Mock weights
        }
        
        with open(filepath, "wb") as f:
            pickle.dump(artifact, f)
            
        print(f"Artifact saved to {filepath}")
        
        job.artifact_path = filepath
        job.status = JobStatus.COMPLETED
        
        # Automatically register the model so it shows up
        # Check if model for this job already exists
        existing_model = db.query(MLModel).filter(MLModel.training_job_id == job.id).first()
        
        if not existing_model:
            new_model = MLModel(
                dataset_id=job.dataset_id,
                asset_type=dataset.domain if dataset and dataset.domain else "Generic",
                model_type=job.model_type,
                algorithm="RandomForest", 
                version="1.0.0",
                accuracy=0.92,
                file_path=filepath,
                active=True,
                deployment_stage="active",
                training_job_id=job.id,
                org_id=job.org_id
            )
            db.add(new_model)
            print(f"Registered new MLModel for Job {job_id}")

        db.commit()
        print(f"Job {job_id} COMPLETED.")
        
    except Exception as e:
        print(f"Pipeline Failed: {e}")
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        db.commit()
