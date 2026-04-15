from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # API Keys
    google_api_key: str

    # App
    app_env: str = "development"
    allowed_origins: str = "http://localhost:3000"

    # Vector store
    chroma_db_path: str = "./chroma_db"

    # Models
    gemini_model: str = "gemini-2.0-flash"
    embedding_model: str = "BAAI/bge-small-en-v1.5"

    # RAG
    rag_top_k: int = 5
    chunk_size: int = 512
    chunk_overlap: int = 64

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
