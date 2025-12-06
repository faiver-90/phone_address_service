"""
Business logic for working with phone-address records.

This layer hides the details of Redis interaction from API handlers and
implements all rules related to creation, update, retrieval and deletion
of phone-address pairs.
"""

from typing import Final

from redis.asyncio import Redis

from app.schemas.phone_address import PhoneAddressCreate, PhoneAddressRead


class PhoneAddressService:
    """Service responsible for managing phone-address records in Redis."""

    def __init__(self, redis_client: Redis) -> None:
        """Initialize the service with a Redis client instance.

        Args:
            redis_client: An asynchronous Redis client used as the underlying
                storage backend.
        """

        self._redis: Final[Redis] = redis_client

    @staticmethod
    def _make_key(phone: str) -> str:
        """Build a Redis key for a given phone number.

        Args:
            phone: Phone number that should be used as a storage key.

        Returns:
            str: A namespaced Redis key.
        """

        return f"phone_address:{phone}"

    async def get(self, phone: str) -> PhoneAddressRead | None:
        """Retrieve phone-address record by phone number.

        Args:
            phone: Phone number to search for.

        Returns:
            PhoneAddressRead | None: A populated model when the record exists
            or ``None`` when no data is found.
        """

        key = self._make_key(phone)
        address = await self._redis.get(key)
        if address is None:
            return None
        return PhoneAddressRead(phone=phone, address=address)

    async def create(self, data: PhoneAddressCreate) -> bool:
        """Create a new phone-address record.

        The method uses the Redis ``SETNX`` command semantics: the record is
        created only if the key does not already exist.

        Args:
            data: Validated payload with ``phone`` and ``address`` fields.

        Returns:
            bool: ``True`` if a new record was created, ``False`` if a record
            with the same phone number already exists.
        """

        key = self._make_key(data.phone)
        # set(name, value, nx=True) -> only set if key does not exist
        was_set: bool | None = await self._redis.set(key, data.address, nx=True)
        return bool(was_set)

    async def update(self, phone: str, address: str) -> bool:
        """Update address for an existing phone number.

        Args:
            phone: Phone number whose address must be updated.
            address: New address value.

        Returns:
            bool: ``True`` if the record existed and was updated, ``False`` if
            no such phone number was found.
        """

        key = self._make_key(phone)

        exists = await self._redis.exists(key)
        if not exists:
            return False
        await self._redis.set(key, address)
        return True

    async def delete(self, phone: str) -> bool:
        """Delete phone-address record from storage.

        Args:
            phone: Phone number whose record should be removed.

        Returns:
            bool: ``True`` if the record existed and was deleted, ``False`` if
            there was nothing to delete.
        """

        key = self._make_key(phone)
        deleted_count = await self._redis.delete(key)
        return bool(deleted_count > 0)
