import time
from db.session import SessionLocal
from models.ml import TrainingJob, JobStatus
from pipelines import manager

def start_worker():
    print("Starting Training Worker...")
    while True:
        db = SessionLocal()
        try:
            # Fetch pending job
            job = db.query(TrainingJob).filter(TrainingJob.status == JobStatus.PENDING).first()
            if job:
                print(f"Updates job {job.id} to RUNNING")
                manager.run_training_pipeline(job.id, db)
            else:
                time.sleep(5)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
        finally:
            db.close()

if __name__ == "__main__":
    start_worker()
