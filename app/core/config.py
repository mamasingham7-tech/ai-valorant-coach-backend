import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# ── Locate .env robustly regardless of working directory ─────────────────────
# Walk up from this file's location to find the .env file
_HERE = Path(__file__).resolve()
for _parent in [_HERE.parent, _HERE.parent.parent, _HERE.parent.parent.parent, _HERE.parent.parent.parent.parent]:
    _candidate = _parent / ".env"
    if _candidate.exists():
        _ENV_FILE = str(_candidate)
        break
else:
    _ENV_FILE = ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore"
    )

    ENVIRONMENT: str = Field(default="development")
    LOG_LEVEL: str = Field(default="INFO")

    # Database Settings
    DATABASE_URL: str = Field(default="postgresql+asyncpg://postgres:postgres@localhost:5432/valorant_coach")
    DB_USER: str = Field(default="postgres")
    DB_PASSWORD: str = Field(default="postgres")
    DB_HOST: str = Field(default="localhost")
    DB_PORT: int = Field(default=5432)
    DB_NAME: str = Field(default="valorant_coach")
    USE_SQLITE: bool = Field(default=True)  # default True so dev works without Postgres

    # Redis Settings
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # Security — strong built-in default for local dev so startup never fails
    JWT_SECRET: str = Field(default="ai-valorant-coach-dev-secret-key-32chars!!")
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)
    ADMIN_EMAIL: str = Field(default="")

    # API Keys
    RIOT_API_KEY: str = Field(default="")
    TRACKER_GG_API_KEY: str = Field(default="")
    HENRIK_API_KEY: str = Field(default="")  # Free key from https://app.henrikdev.xyz
    USE_MOCK_PROVIDER: bool = Field(default=True)

    # CORS — allow frontend dev server
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "*"]

    @property
    def async_database_url(self) -> str:
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

settings = Settings()
