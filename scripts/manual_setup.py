from db.session import engine
from sqlalchemy import text
from core import security
import uuid

def manual_insert():
    with engine.connect() as conn:
        try:
            # 1. Ensure Org exists
            org_name = "Forsee Admin Org"
            check_org = conn.execute(text("SELECT id FROM organization WHERE name = :name"), {"name": org_name}).first()
            
            if not check_org:
                org_id = str(uuid.uuid4())
                conn.execute(
                    text("INSERT INTO organization (id, name, created_at, updated_at) VALUES (:id, :name, now(), now())"),
                    {"id": org_id, "name": org_name}
                )
                print(f"Created Org ID: {org_id}")
            else:
                org_id = check_org[0]
                print(f"Using Existing Org ID: {org_id}")
            
            # 2. Ensure Admin User exists
            email = "admin@forsee.ai"
            check_user = conn.execute(text("SELECT id FROM \"user\" WHERE email = :email"), {"email": email}).first()
            
            if not check_user:
                user_id = str(uuid.uuid4())
                hashed_pw = security.get_password_hash("password123")
                conn.execute(
                    text("INSERT INTO \"user\" (id, email, hashed_password, full_name, role, org_id, is_active, created_at, updated_at) "
                         "VALUES (:id, :email, :pw, :name, :role, :org_id, true, now(), now())"),
                    {
                        "id": user_id,
                        "email": email,
                        "pw": hashed_pw,
                        "name": "System Admin",
                        "role": "ADMIN",
                        "org_id": org_id
                    }
                )
                print(f"Created Admin User: {email}")
            else:
                print(f"Admin User {email} already exists.")
            
            conn.commit()
            print("DONE: DATABASE COMMITTED")
        except Exception as e:
            print(f"SQL Error: {e}")
            conn.rollback()

if __name__ == "__main__":
    manual_insert()
