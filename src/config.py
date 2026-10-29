"""Application configuration loaded from environment variables."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


def _is_placeholder(value: Optional[str]) -> bool:
    if not value:
        return True
    lowered = value.lower()
    placeholders = ("your-", "-here", "password", "sk-your", "changeme", "example")
    return any(p in lowered for p in placeholders)


class Settings(BaseSettings):
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    cohere_api_key: str = Field(default="", alias="COHERE_API_KEY")
    cohere_rerank_api_key: str = Field(default="", alias="COHERE_RERANK_API_KEY")

    llm_model: str = Field(default="gpt-4o-mini", alias="LLM_MODEL")
    embedding_model: str = Field(default="text-embedding-3-large", alias="EMBEDDING_MODEL")
    max_tokens: int = Field(default=4096, alias="MAX_TOKENS")
    temperature: float = Field(default=0.1, alias="TEMPERATURE")

    qdrant_host: str = Field(default="localhost", alias="QDRANT_HOST")
    qdrant_port: int = Field(default=6333, alias="QDRANT_PORT")
    qdrant_api_key: Optional[str] = Field(default=None, alias="QDRANT_API_KEY")
    pgvector_connection_url: Optional[str] = Field(default=None, alias="PGVECTOR_CONNECTION_URL")

    neo4j_uri: str = Field(default="bolt://localhost:7687", alias="NEO4J_URI")
    neo4j_username: str = Field(default="neo4j", alias="NEO4J_USERNAME")
    neo4j_password: str = Field(default="", alias="NEO4J_PASSWORD")

    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_password: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")

    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    next_public_base_url: str = Field(default="http://localhost:3000", alias="NEXT_PUBLIC_BASE_URL")
    next_public_api_url: str = Field(default="http://localhost:8000", alias="NEXT_PUBLIC_API_URL")

    model_config = {"env_file": ".env", "extra": "ignore", "populate_by_name": True}

    @property
    def openai_configured(self) -> bool:
        return not _is_placeholder(self.openai_api_key)

    @property
    def cohere_configured(self) -> bool:
        key = self.cohere_rerank_api_key or self.cohere_api_key
        return not _is_placeholder(key)

    @property
    def neo4j_configured(self) -> bool:
        return not _is_placeholder(self.neo4j_password)

    @property
    def qdrant_configured(self) -> bool:
        return bool(self.qdrant_host)

    def as_dict(self) -> dict:
        return self.model_dump()


_settings = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        env_path = Path(__file__).resolve().parents[1] / ".env"
        # project root is parent of src
        env_path = Path(__file__).resolve().parents[2] / ".env"
        _settings = Settings(_env_file=str(env_path) if env_path.exists() else None)
    return _settings