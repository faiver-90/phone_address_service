from fastapi import Depends
from redis.asyncio import Redis

from app.core.redis import redis_connector
from app.services.phone_address_service import PhoneAddressService


def get_redis_client() -> Redis:
    """FastAPI dependency that returns a shared Redis client instance.

    Returns:
        Redis: Asynchronous Redis client used by the service layer.
    """

    return redis_connector.client


def get_phone_address_service(
    redis_client: Redis = Depends(get_redis_client),
) -> PhoneAddressService:
    """Dependency provider for :class:`PhoneAddressService`.

    Args:
        redis_client: Asynchronous Redis client provided by FastAPI.

    Returns:
        PhoneAddressService: A configured service instance.
    """

    return PhoneAddressService(redis_client=redis_client)
