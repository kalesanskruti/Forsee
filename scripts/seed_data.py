from sqlalchemy.orm import Session
from models.ml import Dataset, InputSchema
from db.session import SessionLocal

def seed_data(db: Session):
    # 1. Seed Input Schemas
    schemas = [
        {
            "name": "Generic Rotating Equipment",
            "system_type": "Motor",
            "schema_definition": {"vibration": "float", "temperature": "float", "rpm": "float"}
        },
        {
            "name": "Turbofan Engine",
            "system_type": "Engine",
            "schema_definition": {f"sensor_{i}": "float" for i in range(1, 22)}
        },
        {
             "name": "Wind Turbine Gearbox",
             "system_type": "Wind Turbine",
             "schema_definition": {"bearing_temp": "float", "oil_pressure": "float", "rotor_speed": "float"}
        }
    ]
    
    for s in schemas:
        if not db.query(InputSchema).filter(InputSchema.name == s["name"]).first():
            db.add(InputSchema(**s))
    
    # 2. Seed Datasets (Metadata only, assuming files exist or will be connector-loaded)
    datasets = [
        {
            "name": "NASA CMAPSS",
            "domain": "Aerospace",
            "industry": "Aerospace",
            "data_type": "timeseries",
            "task_type": "RUL",
            "source_type": "remote",
            "source_path": "https://ti.arc.nasa.gov/c/6/",
            "is_public": True,
            "temporal": True,
            "recommended_window_size": 30
        },
        {
            "name": "AI4I 2020 Predictive Maintenance",
            "domain": "Manufacturing",
            "industry": "Manufacturing",
            "data_type": "tabular",
            "task_type": "CLASSIFICATION", # Multi-class failure
            "source_type": "remote",
            "source_path": "UCI Repository",
            "is_public": True,
            "temporal": False
        },
        {
            "name": "MetroPT-3 Dataset",
            "domain": "Transportation",
            "industry": "Railways",
            "data_type": "timeseries",
            "task_type": "RUL", 
            "source_type": "remote",
            "source_path": "Zenodo",
            "is_public": True,
            "temporal": True
        }
    ]

    for d in datasets:
        if not db.query(Dataset).filter(Dataset.name == d["name"]).first():
            db.add(Dataset(**d))

    db.commit()
    print("Seeding complete.")

if __name__ == "__main__":
    db = SessionLocal()
    seed_data(db)
    db.close()
