import pytest
from httpx import AsyncClient

from app.core.config import get_settings
from app.main import app


@pytest.mark.anyio
async def test_health_endpoint(async_client: AsyncClient) -> None:
    """Проверяем, что /health доступен и возвращает ожидаемый json."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "redis": "ok"}


def test_app_title_matches_settings() -> None:
    """У приложения title должен совпадать с PROJECT_NAME из настроек."""
    settings = get_settings()
    assert app.title == settings.project_name
