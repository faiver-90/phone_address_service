import pytest

from app.schemas.phone_address import PhoneAddressCreate
from app.services.phone_address_service import PhoneAddressService


class InMemoryRedis:
    """In-memory Redis для unit-тестов сервиса (без FastAPI).

    Нужен отдельно от FakeRedis в conftest.py, чтобы не тянуть FastAPI сюда.
    Поведение аналогично: поддерживает get/set(nx)/exists/delete.
    """

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


@pytest.fixture
def in_memory_redis() -> InMemoryRedis:
    return InMemoryRedis()


@pytest.fixture
def service(in_memory_redis: InMemoryRedis) -> PhoneAddressService:
    return PhoneAddressService(redis_client=in_memory_redis)  # type: ignore[arg-type]


@pytest.mark.anyio
@pytest.mark.parametrize(
    "phone,address",
    [
        ("+7 999 111-11-11", "Moscow, Tverskaya 1"),
        ("+7 921 222-22-22", "Saint-Petersburg, Nevsky 10"),
        ("380501234567", "Kyiv, Khreschatyk 5"),
    ],
)
async def test_create_and_get(service: PhoneAddressService, phone: str, address: str) -> None:
    """Создание новой записи и последующее чтение должны работать корректно."""
    created = await service.create(PhoneAddressCreate(phone=phone, address=address))
    assert created is True

    stored = await service.get(phone)
    assert stored is not None
    assert stored.phone == phone
    assert stored.address == address


@pytest.mark.anyio
async def test_create_conflict_on_existing_phone(service: PhoneAddressService) -> None:
    """Повторное создание с тем же номером должно возвращать False."""
    phone = "123"
    address1 = "Addr1"
    address2 = "Addr2"

    created_first = await service.create(PhoneAddressCreate(phone=phone, address=address1))
    created_second = await service.create(PhoneAddressCreate(phone=phone, address=address2))

    assert created_first is True
    assert created_second is False

    stored = await service.get(phone)
    assert stored is not None
    assert stored.address == address1  # Второе создание не должно затирать адрес.


@pytest.mark.anyio
async def test_update_existing_phone(service: PhoneAddressService) -> None:
    """Обновление существующей записи должно менять адрес и возвращать True."""
    phone = "555"
    old_address = "Old addr"
    new_address = "New addr"

    await service.create(PhoneAddressCreate(phone=phone, address=old_address))
    updated = await service.update(phone=phone, address=new_address)
    assert updated is True

    stored = await service.get(phone)
    assert stored is not None
    assert stored.address == new_address


@pytest.mark.anyio
async def test_update_non_existing_phone_returns_false(service: PhoneAddressService) -> None:
    """Попытка обновления несуществующего номера должна вернуть False."""
    updated = await service.update(phone="unknown", address="addr")
    assert updated is False


@pytest.mark.anyio
async def test_delete_existing_phone(service: PhoneAddressService) -> None:
    """Удаление существующего номера должно возвращать True."""
    phone = "777"
    await service.create(PhoneAddressCreate(phone=phone, address="addr"))

    deleted = await service.delete(phone)
    assert deleted is True

    # Повторное удаление должно вернуть False
    deleted_again = await service.delete(phone)
    assert deleted_again is False


@pytest.mark.anyio
async def test_delete_non_existing_phone_returns_false(service: PhoneAddressService) -> None:
    """Удаление несуществующего номера возвращает False."""
    deleted = await service.delete("no-such-phone")
    assert deleted is False
