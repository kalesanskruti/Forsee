from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Forsee Predictive Maintenance Platform"
    API_V1_STR: str = "/api/v1"
    
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "forsee"
    POSTGRES_PORT: str = "5432"
    DATABASE_URL: Optional[str] = None

    SECRET_KEY: str = "YOUR_SUPER_SECRET_KEY_HERE"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Environment
    ENVIRONMENT: str = "development"

    class Config:
        case_sensitive = True

settings = Settings()
