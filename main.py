from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from api.api import api_router
from core.config import settings
from api.middleware import OperationalMiddleware
from core.ratelimit import limiter, _rate_limit_exceeded_handler, RateLimitExceeded

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Set all CORS enabled, valid for this assignment
app.add_middleware(OperationalMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Metrics
Instrumentator().instrument(app).expose(app)

@app.on_event("startup")
def on_startup():
    # Initialize TimescaleDB (ensure extension and hypertables)
    from db.session import SessionLocal
    from db.timescaledb import init_timescaledb
    db = SessionLocal()
    try:
        init_timescaledb(db)
    except Exception as e:
        print(f"DB INIT SKIPPED: {e}")
    finally:
        db.close()

@app.get("/health")
def health_check():
    return {"status": "ok"}


