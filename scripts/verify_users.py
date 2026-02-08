from db.session import SessionLocal
from sqlalchemy import text

def verify():
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT email FROM \"user\"")).all()
        print(f"Users in DB: {[r[0] for r in result]}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify()
