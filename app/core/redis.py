"""
Redis client initialization and lifecycle management.

This module provides a single shared Redis client instance that is
created on application startup and closed on shutdown.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import redis.asyncio as redis
from fastapi import FastAPI

from app.core.config import get_redis_url

RedisClient = redis.Redis


class RedisConnector:
    """High-level wrapper responsible for managing Redis client lifecycle.

    The connector lazily initializes a :class:`redis.asyncio.Redis` client
    using configuration provided by :mod:`app.core.config`.
    """

    def __init__(self) -> None:
        """Initialize the connector without creating a client yet."""
        self._client: RedisClient | None = None

    @property
    def client(self) -> RedisClient:
        """Return an initialized Redis client.

        The client is created on first access. If initialization fails, an
        exception from the underlying :mod:`redis` library is raised.

        Returns:
            RedisClient: Shared Redis client instance.
        """

        if self._client is None:
            self._client = redis.from_url(get_redis_url(), decode_responses=True)
        return self._client

    async def close(self) -> None:
        """Close the Redis client connection pool if it was created."""

        if self._client is not None:
            await self._client.aclose()
            self._client = None


redis_connector = RedisConnector()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[dict[str, Any]]:
    """Application lifespan manager for FastAPI.

    This function is used as a lifespan context manager in the FastAPI
    application. It ensures that Redis resources are properly cleaned up
    on application shutdown.

    Args:
        app: The FastAPI application instance.

    Yields:
        dict[str, Any]: A mutable state dictionary, currently unused but can
        be used in future for shared resources.
    """

    state: dict[str, Any] = {}
    try:
        yield state
    finally:
        await redis_connector.close()
