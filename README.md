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

## Setup

1. **Environment Variables**:
   Copy `.env.example` to `.env` and fill in the values.

2. **Database Migrations (Alembic)**:
   We use Alembic for database migrations.
   
   Initialize alembic (if not already):
   ```bash
   alembic init alembic
   ```
   
   Update `alembic.ini` to point to your DB or use `env.py` to load from `core.config`.
   
   Generate a migration for the new SaaS tables:
   ```bash
   alembic revision --autogenerate -m "initial_saas_schema"
   ```
   
   Apply migrations:
   ```bash
   alembic upgrade head
   ```

3. **Running**:
   ```bash
   docker-compose up --build
   ```

## Key Features
- **Multi-tenancy**: All resources are isolated by `org_id`.
- **RBAC**: Roles (ADMIN, ENGINEER, VIEWER) enforce permissions.
- **ML Lifecycle**: Registries for Datasets, Models, and Assets.
- **Training Pipelines**: Async job tracking.
- **Audit Logging**: Comprehensive action logging.

