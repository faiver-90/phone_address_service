from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.v1.deps import get_redis_client
from app.main import app


class FakeRedis:
    """The simplest in-memory Redis alternative for testing."""

    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    async def get(self, name: str) -> str | None:
        return self._store.get(name)

    async def set(self, name: str, value: str, nx: bool | None = None) -> bool:
        if nx:
            if name in self._store:
                return False
            self._store[name] = value
            return True
        self._store[name] = value
        return True

    async def exists(self, name: str) -> int:
        return int(name in self._store)

    async def delete(self, name: str) -> int:
        return int(self._store.pop(name, None) is not None)

    async def ping(self) -> bool:
        """Эмуляция redis.ping() — в тестах всегда 'живой'."""
        return True


@pytest.fixture
def fake_redis() -> FakeRedis:
    return FakeRedis()


@pytest.fixture(autouse=True)
def override_redis_dependency(fake_redis: FakeRedis) -> Generator[None, None, None]:
    """Replace the get_redis_client dependency with fake_redis for all tests."""

    def _get_fake_redis() -> FakeRedis:
        return fake_redis

    app.dependency_overrides[get_redis_client] = _get_fake_redis
    yield
    app.dependency_overrides.pop(get_redis_client, None)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, Any]:
    """HTTP client for testing FastAPI applications."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
