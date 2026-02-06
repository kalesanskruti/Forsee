import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pipelines.manager import run_training_pipeline
from models.ml import TrainingJob, JobStatus, Dataset, MLModel
from uuid import uuid4
from collections import namedtuple
import uuid

# Mock Job and DB Session
# Mock Session with smarter query handling
class MockSession:
    def __init__(self):
        self.current_job = None
        self.current_dataset = None
        self.last_model = None
    
    def query(self, model):
        self.last_model = model
        return self
    
    def filter(self, condition):
        return self
        
    def first(self):
        # Return appropriate mock object based on what was queried
        if self.last_model.__name__ == "Dataset":
            return self.current_dataset
        return self.current_job
        
    def add(self, obj):
        pass

    def commit(self):
        pass
        
    def refresh(self, obj):
        pass

def run_manual_training():
    print("Executing Manual Training Run for ALL DATASETS...")
    
    # Clean up old models to avoid confusion
    import os
    import shutil
    models_dir = "datasets/models"
    if os.path.exists(models_dir):
        print("Cleaning up old model files...")
        shutil.rmtree(models_dir)
    os.makedirs(models_dir, exist_ok=True)
    
    dataset_tasks = [
        ("NASA_CMAPSS", "LSTM_RUL"),
        ("AI4I_2020", "XGBoost_Classification"),
        ("SCANIA_Component_X", "RandomForest_Cost"),
        ("MetroPT", "GradientBoosting_Predictive"),
        ("MIMII_Acoustic", "Autoencoder_Anomaly"),
        ("PHM_Public", "CNN_Fault"),
        ("Awesome_Datasets", "General_Regression")
    ]
    
    db = MockSession()
    from models.ml import Dataset # Ensure comparison works

    for name, model_type in dataset_tasks:
        print(f"\n--- Training for {name} ---")
        
        # 1. Create a job for this dataset
        class Job:
            def __init__(self, mtype):
                self.id = uuid.uuid4()
                self.dataset_id = uuid.uuid4() # Mock ID
                self.model_type = mtype
                self.status = JobStatus.PENDING
                self.artifact_path = None
                self.error_message = None
                self.org_id = uuid.uuid4()
        
        class MockDataset:
            def __init__(self, n):
                self.name = n
                self.domain = "Generic"
                self.id = uuid.uuid4()
        
        job = Job(model_type)
        dataset = MockDataset(name)
        
        db.current_job = job
        db.current_dataset = dataset
        
        print(f"Created Job ID: {job.id}")
        
        # 3. Run Pipeline
        run_training_pipeline(job.id, db)
    
    print("\nAll Datasets Processed. Check datasets/models/ folder.")

if __name__ == "__main__":
    run_manual_training()
