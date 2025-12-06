import pytest

from app.core.config import Settings


def test_settings_defaults() -> None:
    """Checking the default values for the settings."""
    settings = Settings()
    assert settings.project_name == "Phone Address Service"
    assert settings.api_v1_prefix == "/api/v1"
    assert settings.redis_url == "redis://redis:6379/0"


def test_settings_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """Environment variables should override default values.."""
    monkeypatch.setenv("PROJECT_NAME", "Custom Service")
    monkeypatch.setenv("API_V1_PREFIX", "/custom")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6380/1")

    settings = Settings()

    assert settings.project_name == "Custom Service"
    assert settings.api_v1_prefix == "/custom"
    assert settings.redis_url == "redis://localhost:6380/1"
