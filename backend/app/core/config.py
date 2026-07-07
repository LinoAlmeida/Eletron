from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Eletron Reservas"
    app_env: str = "development"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60
    database_url: str = "postgresql+psycopg://eletron:eletron_dev@127.0.0.1:5433/eletron"
    legacy_database_url: str = "postgresql://eletron:eletron_dev@127.0.0.1:5433/eletron"
    backend_cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    oracle_user: str | None = None
    oracle_password: str | None = None
    oracle_dsn: str | None = None
    oracle_client_lib_dir: str | None = None

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
