import sys
import os
sys.path.append(os.getcwd())

from db.session import SessionLocal
from models.user import User, Organization, Role
from core import security
import uuid

def main():
    db = SessionLocal()
    try:
        # 1. Org
        org = db.query(Organization).filter(Organization.name == "Main Org").first()
        if not org:
            org = Organization(name="Main Org")
            db.add(org)
            db.commit()
            db.refresh(org)
            print(f"Created Org: {org.id}")
        else:
            print(f"Found Org: {org.id}")

        # 2. User
        email = "admin@forsee.ai"
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                hashed_password=security.get_password_hash("password123"),
                full_name="Admin",
                role=Role.ADMIN,
                org_id=org.id,
                is_active=True
            )
            db.add(user)
            db.commit()
            print(f"Created User: {email}")
        else:
            print(f"User {email} already exists.")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
