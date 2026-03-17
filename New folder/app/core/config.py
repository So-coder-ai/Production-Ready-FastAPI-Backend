from __future__ import annotations

from pydantic import AnyUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "fastapi-backend"
    environment: str = Field(default="local", description="local|staging|prod")
    log_level: str = Field(default="INFO", description="DEBUG|INFO|WARNING|ERROR")

    api_prefix: str = "/api/v1"

    jwt_secret_key: str = Field(default="change-me-please-change-me", min_length=16)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    cors_allow_origins: list[str] = Field(default_factory=lambda: ["*"])

    @field_validator("cors_allow_origins", mode="before")
    @classmethod
    def _parse_cors_allow_origins(cls, v):
        if v is None:
            return ["*"]
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            s = v.strip()
            if not s:
                return ["*"]
            if s == "*":
                return ["*"]
            return [part.strip() for part in s.split(",") if part.strip()]
        return v

    database_url: AnyUrl = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/app",
        description="SQLAlchemy URL (psycopg recommended).",
    )


settings = Settings()
