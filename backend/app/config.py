from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent  # backend/


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(BACKEND_DIR / ".env"), extra="ignore")

    APP_ENV: str = "development"
    DATABASE_URL: str = "postgresql://sustaina:sustaina@localhost:5432/sustaina"
    NEXT_PUBLIC_API_URL: str = "http://localhost:8000"
    FORCE_DEMO_MODE: bool = False

    NEXT_PUBLIC_MAPBOX_TOKEN: str = ""
    COPERNICUS_CLIENT_ID: str = ""
    COPERNICUS_CLIENT_SECRET: str = ""
    DATA_GOV_API_KEY: str = ""
    OPENTOPOGRAPHY_API_KEY: str = ""
    GOOGLE_MAPS_API_KEY: str = ""
    GEMINI_API_KEY: str = ""


settings = Settings()
