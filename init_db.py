from sqlalchemy import create_engine
from core.config import settings

# Wait for DB to be ready and create tables
try:
    from db.base_class import Base
    from models import user, ml, platform
    from db.session import engine
    
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")
    
    # Init Timescale
    from db.timescaledb import init_timescaledb
    from db.session import SessionLocal
    db = SessionLocal()
    init_timescaledb(db)
    db.close()
    
except Exception as e:
    print(f"Initialization Failed: {e}")
