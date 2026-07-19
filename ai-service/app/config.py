from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://helpdesk:helpdesk@localhost:5432/ai_db"
    jwt_secret: str = "dev-secret-change-me-please-32-bytes-min!"
    jwt_algorithm: str = "HS256"
    service_token_ttl_seconds: int = 300

    google_api_key: str = ""
    gemini_chat_model: str = "gemini-2.5-flash"
    gemini_embedding_model: str = "models/gemini-embedding-001"
    embedding_dims: int = 768

    ticket_api_url: str = "http://localhost:8082"
    slack_webhook_url: str = ""
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_from: str = "ai-helpdesk@helpdesk.local"

    ai_agent_user_id: int = 9000
    ai_agent_email: str = "ai@helpdesk.local"

    cors_allowed_origins: str = "http://localhost:5173"
    knowledge_base_dir: str = "/knowledge-base"

    retrieval_top_k: int = 5
    queue_poll_interval_seconds: float = 2.0

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]

    @property
    def sync_database_url(self) -> str:
        """psycopg URL for the LangGraph checkpointer (it uses psycopg, not asyncpg)."""
        return self.database_url.replace("postgresql+asyncpg://", "postgresql://")


@lru_cache
def get_settings() -> Settings:
    return Settings()
