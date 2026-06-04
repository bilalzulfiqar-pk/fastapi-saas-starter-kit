from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FastAPI SaaS Starter Kit"
    app_env: str = "development"
    app_url: str = "http://localhost:3000"
    api_url: str = "http://localhost:8000"
    database_url: str = "postgresql+psycopg://postgres:postgres@db:5432/saas_starter"
    secret_key: str = "change-me-please-with-at-least-32-bytes"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    cookie_domain: str = ""
    cookie_secure: bool = False
    cookie_samesite: str = "lax"
    access_cookie_name: str = "saas_access_token"
    refresh_cookie_name: str = "saas_refresh_token"
    frontend_origins: str = Field(default="http://localhost:3000,http://web:3000")
    redis_url: str = "redis://redis:6379/0"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    @property
    def trusted_origins(self) -> list[str]:
        values = [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]
        return list(dict.fromkeys(values))

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
