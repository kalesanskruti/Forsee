from sqlalchemy.orm import Session
from models import Organization, User, Role
from db.session import SessionLocal
from core.security import get_password_hash

def create_initial_org(db: Session):
    # 1. Check if Org exits
    org = db.query(Organization).filter(Organization.name == "Forsee Demo Org").first()
    if not org:
        org = Organization(name="Forsee Demo Org")
        db.add(org)
        db.commit()
        db.refresh(org)
        print(f"Created Organization: {org.name}")
    else:
        print(f"Organization already exists: {org.name}")

    # 2. Check if Admin User exists
    user = db.query(User).filter(User.email == "admin@forsee.ai").first()
    if not user:
        user = User(
            email="admin@forsee.ai",
            hashed_password=get_password_hash("password123"),
            full_name="System Admin",
            role=Role.ADMIN,
            org_id=org.id,
            is_active=True
        )
        db.add(user)
        db.commit()
        print(f"Created Admin User: {user.email}")
    else:
        print(f"Admin User already exists: {user.email}")

if __name__ == "__main__":
    db = SessionLocal()
    create_initial_org(db)
    db.close()
