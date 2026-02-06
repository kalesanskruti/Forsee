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
if settings.DATABASE_URL: # Just a check
    pass

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(OperationalMiddleware)

app.include_router(api_router, prefix=settings.API_V1_STR)

# Metrics
Instrumentator().instrument(app).expose(app)

@app.on_event("startup")
def on_startup():
    # Initialize TimescaleDB (ensure extension and hypertables)
    # WARNING: In production, this might be better placed in a migration script.
    from db.session import SessionLocal
    from db.timescaledb import init_timescaledb
    db = SessionLocal()
    try:
        init_timescaledb(db)
    finally:
        db.close()

@app.get("/health")
def health_check():
    return {"status": "ok"}
