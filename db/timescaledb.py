from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

def init_timescaledb(db: Session):
    """
    Enable TimescaleDB extension and convert specific tables to hypertables.
    This should be run after tables are created (e.g., after Alembic upgrade).
    """
    try:
        # 1. Enable Extension
        logger.info("Enabling TimescaleDB extension...")
        db.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"))
        db.commit()
    except Exception as e:
        logger.warning(f"Could not enable TimescaleDB extension (might already exist or permission error): {e}")
        db.rollback()

    # 2. Convert 'prediction' table to hypertable
    # We check if it's already a hypertable to avoid errors
    try:
        logger.info("Converting 'prediction' to hypertable...")
        # Check if already hypertable
        check_query = text("SELECT * FROM timescaledb_information.hypertables WHERE hypertable_name = 'prediction';")
        result = db.execute(check_query).scalar()
        
        if not result:
            # chunk_time_interval = 1 day (typically good starting point for high freq data)
            # 86400000000 microseconds if timestamp is simple... 
            # TimescaleDB defaults are usually smart, but let's be explicit if needed.
            # Using standard execution.
            db.execute(text("SELECT create_hypertable('prediction', 'timestamp');"))
            db.commit()
            logger.info("Successfully converted 'prediction' to hypertable.")
        else:
            logger.info("'prediction' is already a hypertable.")
            
    except Exception as e:
        logger.error(f"Error converting prediction table: {e}")
        db.rollback()

    # 3. Retention Policies (Example: 90 days)
    # db.execute(text("SELECT add_retention_policy('prediction', INTERVAL '90 days');"))

