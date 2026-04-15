from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # API Keys
    google_api_key: str

    # App
    app_env: str = "development"
    allowed_origins: str = "http://localhost:3000"

    # Models
    gemini_model: str = "gemini-2.5-flash"

    # Rate limiting (per IP)
    rate_limit_chat: str = "8/minute"
    rate_limit_chat_daily: str = "100/day"
    rate_limit_ingest: str = "5/hour"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
