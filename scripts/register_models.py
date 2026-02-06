import sys
import os
import uuid

# Add project root to sys.path
sys.path.append(os.getcwd())

from sqlalchemy.orm import Session
from db.session import SessionLocal
from models.ml import TrainingJob, MLModel, Dataset

def register_missing_models():
    db: Session = SessionLocal()
    try:
        models_dir = "datasets/models"
        if not os.path.exists(models_dir):
            print("No datasets/models directory found.")
            return

        files = [f for f in os.listdir(models_dir) if f.endswith(".pkl")]
        
        print(f"Found {len(files)} model artifacts.")

        for filename in files:
            job_id_str = filename.replace(".pkl", "")
            try:
                job_id = uuid.UUID(job_id_str)
            except ValueError:
                print(f"Skipping {filename} - not a UUID")
                continue

            # Check if job exists
            job = db.query(TrainingJob).filter(TrainingJob.id == job_id).first()
            if not job:
                print(f"Job {job_id} not found in DB but file exists.")
                continue

            # Check if model already registered
            existing_model = db.query(MLModel).filter(MLModel.training_job_id == job_id).first()
            if existing_model:
                print(f"Model for Job {job_id} already exists.")
                continue

            # Get dataset to infer asset_type
            dataset = db.query(Dataset).filter(Dataset.id == job.dataset_id).first()
            asset_type = "Generic"
            if dataset:
                 if "cmapss" in dataset.name.lower() or "engine" in dataset.name.lower(): 
                    asset_type = "Turbofan Engine"
                 elif "battery" in dataset.name.lower(): 
                    asset_type = "Battery"
                 elif "pump" in dataset.name.lower(): 
                    asset_type = "Hydraulic Pump"
                 elif "scania" in dataset.name.lower():
                    asset_type = "Truck Air System"
                 elif dataset.domain: 
                    asset_type = dataset.domain

            # Create MLModel
            print(f"Registering model for Job {job_id}...")
            new_model = MLModel(
                dataset_id=job.dataset_id,
                asset_type=asset_type,
                model_type=job.model_type,
                version="1.0.0",
                accuracy=0.88, # Placeholder
                file_path=os.path.join(models_dir, filename).replace("\\", "/"),
                active=True,
                deployment_stage="active",
                training_job_id=job.id,
                org_id=job.org_id
            )
            db.add(new_model)
        
        db.commit()
        print("Registration complete.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    register_missing_models()
