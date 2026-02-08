from sqlalchemy import create_engine, text
import os

DATABASE_URL = "postgresql://postgres:securepassword@localhost:5432/forsee"

def inspect():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("--- TABLE: user ---")
        res = conn.execute(text("SELECT email, role, is_active FROM \"user\""))
        for row in res:
            print(row)
            
        print("--- TABLE: organization ---")
        res = conn.execute(text("SELECT id, name FROM organization"))
        for row in res:
            print(row)

if __name__ == "__main__":
    inspect()
