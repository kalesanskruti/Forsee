# Forsee Predictive Maintenance Platform

## Architecture
This project implements an enterprise-grade multi-tenant SaaS platform around a Predictive Maintenance ML core.

### Layered Structure
- **api/**: FastAPI routers and dependency injection.
- **core/**: Configuration, security, and context management.
- **models/**: SQLAlchemy ORM models (User, Organization, Asset, Model, Dataset, etc.).
- **schemas/**: Pydantic schemas for request/response validation.
- **services/**: Business logic layer.
- **ml/**: Core ML inference engine (mocked for this delivery).
- **pipelines/**: Training pipeline management.
- **db/**: Database session and base classes.

## Tech Stack
- Python 3.9+
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- Docker

## 🚀 Getting Started for Developers

### 1. Clone the Repository
```bash
git clone https://github.com/kalesanskruti/Forsee.git
cd Forsee
```

### 2. Set up Environment
Create a `.env` file in the root directory. You can copy the example:
Windows (PowerShell):
```powershell
Copy-Item .env.example .env
```
Mac/Linux:
```bash
cp .env.example .env
```

### 3. Run with Docker (Recommended)
This will start the Database (PostgreSQL + TimescaleDB) and the API server.
```bash
docker-compose up --build
```
*Wait until you see "Application startup complete" in the logs.*

### 4. Initialize Data (First Time Only)
Open a new terminal window and run the seed script to populate the database with default datasets and schemas:
```bash
# Windows
python scripts/seed_data.py

# Mac/Linux
python3 scripts/seed_data.py
```

### 5. Access the App
- **API Documentation (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Root**: [http://localhost:8000/api/v1](http://localhost:8000/api/v1)

### 6. (Optional) Run Specific Components Locally
If you want to run the API outside of Docker for debugging:
1. Create a virtual environment: `python -m venv .venv`
2. Activate it: `.venv\Scripts\Activate` (Windows) or `source .venv/bin/activate` (Mac/Linux)
3. Install dependencies: `pip install -r requirements.txt`
4. Start the server: `uvicorn main:app --reload`


## Key Features
- **Multi-tenancy**: All resources are isolated by `org_id`.
- **RBAC**: Roles (ADMIN, ENGINEER, VIEWER) enforce permissions.
- **ML Lifecycle**: Registries for Datasets, Models, and Assets.
- **Training Pipelines**: Async job tracking.
- **Audit Logging**: Comprehensive action logging.

