from http import HTTPStatus

import pytest
from httpx import AsyncClient

from tests.conftest import FakeRedis


@pytest.mark.anyio
async def test_create_phone_address_success(async_client: AsyncClient) -> None:
    """Successful creation of a new record returns 201 and the record body."""
    payload = {"phone": "+7 999 000-00-01", "address": "Moscow, Test street 1"}
    response = await async_client.post("/api/v1/phone-addresses", json=payload)

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data["phone"] == payload["phone"]
    assert data["address"] == payload["address"]


@pytest.mark.anyio
async def test_create_phone_address_conflict(
    async_client: AsyncClient, fake_redis: FakeRedis
) -> None:
    """Re-creating the record with the same phone number should return a 409."""

    payload = {"phone": "111", "address": "Addr1"}
    resp1 = await async_client.post("/api/v1/phone-addresses", json=payload)
    assert resp1.status_code == HTTPStatus.CREATED

    resp2 = await async_client.post("/api/v1/phone-addresses", json=payload)
    assert resp2.status_code == HTTPStatus.CONFLICT
    assert resp2.json()["detail"] == "Phone number already exists."


@pytest.mark.anyio
async def test_get_phone_address_found(async_client: AsyncClient) -> None:
    """The GET endpoint must return the record if it exists.."""
    payload = {"phone": "222", "address": "Some address"}
    await async_client.post("/api/v1/phone-addresses", json=payload)

    response = await async_client.get(f"/api/v1/phone-addresses/{payload['phone']}")
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["phone"] == payload["phone"]
    assert data["address"] == payload["address"]


@pytest.mark.anyio
async def test_get_phone_address_not_found(async_client: AsyncClient) -> None:
    """GET по несуществующему номеру должен вернуть 404."""
    response = await async_client.get("/api/v1/phone-addresses/not-exists")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "Phone number not found."


@pytest.mark.anyio
async def test_update_phone_address_success(async_client: AsyncClient) -> None:
    """A successful address update should return 200 and the new address."""
    phone = "333"
    await async_client.post("/api/v1/phone-addresses", json={"phone": phone, "address": "Old"})

    new_payload = {"address": "New Address"}
    response = await async_client.put(f"/api/v1/phone-addresses/{phone}", json=new_payload)
    assert response.status_code == HTTPStatus.OK

    data = response.json()
    assert data["phone"] == phone
    assert data["address"] == new_payload["address"]

    resp_get = await async_client.get(f"/api/v1/phone-addresses/{phone}")
    assert resp_get.status_code == HTTPStatus.OK
    assert resp_get.json()["address"] == new_payload["address"]


@pytest.mark.anyio
async def test_update_phone_address_not_found(async_client: AsyncClient) -> None:
    """Updating a non-existent record should return a 404."""
    response = await async_client.put(
        "/api/v1/phone-addresses/unknown",
        json={"address": "addr"},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "Phone number not found."


@pytest.mark.anyio
async def test_delete_phone_address_success(async_client: AsyncClient) -> None:
    """A successful deletion should return 204 and an empty response.."""
    phone = "444"
    await async_client.post("/api/v1/phone-addresses", json={"phone": phone, "address": "Addr"})

    response = await async_client.delete(f"/api/v1/phone-addresses/{phone}")
    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.text == ""

    response_again = await async_client.delete(f"/api/v1/phone-addresses/{phone}")
    assert response_again.status_code == HTTPStatus.NOT_FOUND
    assert response_again.json()["detail"] == "Phone number not found."


@pytest.mark.anyio
@pytest.mark.parametrize(
    "phone",
    [
        "123",
        "+7 999 123-45-67",
        "380501234567",
    ],
)
async def test_roundtrip_parametrized(async_client: AsyncClient, phone: str) -> None:
    """Parameterized full-loop test: create -> get -> delete."""
    address = f"Address for {phone}"
    resp_create = await async_client.post(
        "/api/v1/phone-addresses",
        json={"phone": phone, "address": address},
    )
    assert resp_create.status_code == HTTPStatus.CREATED

    resp_get = await async_client.get(f"/api/v1/phone-addresses/{phone}")
    assert resp_get.status_code == HTTPStatus.OK
    assert resp_get.json()["address"] == address

    resp_delete = await async_client.delete(f"/api/v1/phone-addresses/{phone}")
    assert resp_delete.status_code == HTTPStatus.NO_CONTENT
