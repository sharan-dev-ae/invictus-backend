from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    data_provider: str = "memory"
    database_url: str | None = None
    supabase_url: str = "https://jdlaylyoixxkcrhftofg.supabase.co"
    supabase_anon_key: str | None = None
    auth_required: bool = True
    planner_provider: str = "rules"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    cors_origins: str = "http://localhost:5173"
    keep_alive_url: str | None = None
    keep_alive_interval_seconds: int = 600
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [value.strip() for value in self.cors_origins.split(",") if value.strip()]

    def validate_provider(self) -> None:
        if self.data_provider not in {"memory", "postgres"}:
            raise ValueError("DATA_PROVIDER must be memory or postgres")
        if self.data_provider == "postgres" and not self.database_url:
            raise ValueError("DATABASE_URL is required when DATA_PROVIDER=postgres")

@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_provider()
    return settings
