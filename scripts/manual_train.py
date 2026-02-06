from pipelines.manager import run_training_pipeline
from models.ml import TrainingJob, JobStatus
from uuid import uuid4
from collections import namedtuple

# Mock Job and DB Session
MockJob = namedtuple("MockJob", ["id", "model_type", "status", "artifact_path", "error_message"])
class MockSession:
    def __init__(self):
        self.jobs = {}
    
    def query(self, model):
        return self
    
    def filter(self, condition):
        # Extremely simplified mock
        return self
        
    def first(self):
        # Return a mock job that acts like the sqlalchemy model
        # We need a mutable object
        class Job:
            def __init__(self):
                self.id = uuid4()
                self.model_type = "LSTM_RUL"
                self.status = JobStatus.PENDING
                self.artifact_path = None
                self.error_message = None
        return Job()
        
    def commit(self):
        pass

def run_manual_training():
    print("Executing Manual Training Run...")
    
    # 1. Create Mock Session
    db = MockSession()
    
    # 2. Get a job (Mock)
    job = db.first()
    print(f"Created Job: {job.id}")
    
    # 3. Run Pipeline
    run_training_pipeline(job.id, db)
    
    print("Manual Run Complete.")

if __name__ == "__main__":
    run_manual_training()
