from sqlalchemy.orm import Session
from models import Asset, Organization, User
from db.session import SessionLocal
import uuid

def seed_assets(db: Session):
    # 1. Get Default Org
    org = db.query(Organization).first()
    if not org:
        print("Error: No Organization found. Please run init_db first or create an admin user.")
        return

    # 2. Define Assets from Frontend Manifest
    assets_data = [
        {
            "name": "Power Transformer",
            "type": "power-transformers",
            "description": "Critical Grid Infrastructure - Tx-Net-v4.2 (DGA)",
            "status": "ONLINE",
            "meta_data": {
                "regime": "Base Load (Continuous)",
                "age": "14.2 Years",
                "lastMaintenance": "3 Months Ago"
            }
        },
        {
            "name": "Wind Turbine",
            "type": "wind-turbines",
            "description": "Renewable Energy Unit - Aero-Dyn-v9 (Vib)",
            "status": "ONLINE",
            "meta_data": {
                "regime": "Variable (High Wind)",
                "age": "6.5 Years",
                "lastMaintenance": "6 Months Ago"
            }
        },
        {
            "name": "Industrial Motor",
            "type": "industrial-motors",
            "description": "HVAC & Manufacturing Driver - Induct-X-v2",
            "status": "ONLINE",
            "meta_data": {
                "regime": "Cyclic Start/Stop",
                "age": "3.1 Years",
                "lastMaintenance": "1 Month Ago"
            }
        },
        {
            "name": "ICU Patient Monitor",
            "type": "icu-monitoring",
            "description": "Critical Care Telemetry - Bio-Sense-AI-v1",
            "status": "ONLINE",
            "meta_data": {
                "regime": "Triage: Critical",
                "age": "N/A",
                "lastMaintenance": "Daily Calib"
            }
        },
        {
            "name": "Data Center Server",
            "type": "servers",
            "description": "High-Performance Compute Node - Blade-X9",
            "status": "ONLINE",
            "meta_data": {
                "regime": "Peak Load",
                "age": "1.5 Years",
                "lastMaintenance": "2 Weeks Ago"
            }
        }
    ]

    print(f"Seeding assets for Organization: {org.name} ({org.id})")

    for asset_def in assets_data:
        # Check if exists by type/name
        existing = db.query(Asset).filter(Asset.name == asset_def["name"], Asset.org_id == org.id).first()
        if existing:
            print(f"Skipping {asset_def['name']} (Already exists: {existing.id})")
            continue
        
        asset = Asset(
            org_id=org.id,
            name=asset_def["name"],
            type=asset_def["type"],
            description=asset_def["description"],
            status=asset_def["status"],
            # meta_data=asset_def["meta_data"]
        )
        db.add(asset)
        print(f"Created asset: {asset.name}")

    db.commit()
    print("Asset seeding complete.")

if __name__ == "__main__":
    db = SessionLocal()
    seed_assets(db)
    db.close()
