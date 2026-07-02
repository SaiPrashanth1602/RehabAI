"""
config.py

Application configuration.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ----------------------------
    # Project
    # ----------------------------
    PROJECT_NAME: str = "RehabAI Backend API"
    VERSION: str = "1.0"

    # ----------------------------
    # API
    # ----------------------------
    API_V1_STR: str = "/api/v1"

    # ----------------------------
    # CORS
    # ----------------------------
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )


settings = Settings()