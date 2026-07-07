from functools import lru_cache

from pydantic import Field
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Eletron Reservas"
    app_env: str = "development"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60
    database_url: str = "postgresql+psycopg://eletron:eletron_dev@127.0.0.1:5432/eletron"
    legacy_database_url: str = "postgresql://eletron:eletron_dev@127.0.0.1:5432/eletron"
    backend_cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"]
    )

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
