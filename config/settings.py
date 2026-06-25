"""Application settings loaded from environment variables."""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    SERVICE_NAME: str = "a2a-mcp"
    DEBUG_MODE: bool = False
    HOT_RELOAD: bool = False
    ALLOWED_ORIGINS: List[str] = ["*"]

    # Optional Redis — enables multi-worker session tracking.
    # If unset, an in-process dict is used (single-worker / dev deployments).
    REDIS_URL: str = ""  # e.g. redis://localhost:6379/0

    # Optional AI provider keys (used only by skills that need them).
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
