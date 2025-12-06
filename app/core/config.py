"""
Application configuration module.

This module defines the Settings class, which is responsible for loading
configuration from environment variables (including the .env file).
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        project_name: Human-readable name of the service.
        api_v1_prefix: URL prefix for all v1 API endpoints.
        redis_url: Connection URL for the Redis instance.
    """

    project_name: str = "Phone Address Service"
    api_v1_prefix: str = "/api/v1"
    redis_url: str = "redis://redis:6379/0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings instance.

    The function is wrapped with :func:`functools.lru_cache` to avoid
    re-reading environment variables on every call.

    Returns:
        Settings: A singleton instance of application settings.
    """

    return Settings()


def get_redis_url() -> str:
    """Return Redis connection URL from settings.

    Returns:
        str: Redis connection URI string compatible with redis-py.
    """

    settings = get_settings()
    return settings.redis_url
