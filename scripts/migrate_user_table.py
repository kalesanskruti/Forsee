from sqlalchemy import text
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.session import engine

def migrate_user_table():
    print("Migrating User table to support Google Auth...")
    with engine.connect() as connection:
        # Check if column exists to avoid error
        try:
            # We wrap in transaction
            trans = connection.begin()
            
            # Check for oauth_provider
            # This is a naive check, for PostgreSQL specifically
            check_sql = text("SELECT column_name FROM information_schema.columns WHERE table_name='user' AND column_name='oauth_provider';")
            result = connection.execute(check_sql).fetchone()
            
            if not result:
                print("Adding oauth_provider column...")
                connection.execute(text("ALTER TABLE \"user\" ADD COLUMN oauth_provider VARCHAR DEFAULT 'local';"))
            else:
                print("oauth_provider column already exists.")

            # Check for oauth_provider_id
            check_sql_id = text("SELECT column_name FROM information_schema.columns WHERE table_name='user' AND column_name='oauth_provider_id';")
            result_id = connection.execute(check_sql_id).fetchone()
            
            if not result_id:
                print("Adding oauth_provider_id column...")
                connection.execute(text("ALTER TABLE \"user\" ADD COLUMN oauth_provider_id VARCHAR;"))
            else:
                print("oauth_provider_id column already exists.")
                
            trans.commit()
            print("Migration successful.")
            
        except Exception as e:
            print(f"Migration failed: {e}")
            # trans.rollback() # Context manager handles rollback on error usually, or explicit needed? 
            # connection.begin() context manager commits on success, rolls back on exception.
            # But here `engine.connect()` provides connection. `connection.begin()` returns a transaction.
            raise e

if __name__ == "__main__":
    migrate_user_table()
