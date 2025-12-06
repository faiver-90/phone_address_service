"""
API routes for managing phone-address records.

All endpoints in this module are grouped under the `/phone-addresses` prefix
and documented via FastAPI's OpenAPI/Swagger integration.
"""

from http import HTTPStatus

from fastapi import APIRouter, Depends, Path

from app.api.v1.deps import get_phone_address_service
from app.schemas.phone_address import (
    ErrorResponse,
    PhoneAddressCreate,
    PhoneAddressRead,
    PhoneAddressUpdate,
)
from app.services.phone_address_service import PhoneAddressService

router = APIRouter(prefix="/phone-addresses", tags=["Phone-address management"])


@router.get(
    "/{phone}",
    response_model=PhoneAddressRead,
    responses={
        HTTPStatus.NOT_FOUND.value: {
            "model": ErrorResponse,
            "description": "Phone number was not found in the storage.",
        },
    },
    summary="Get address by phone number",
    description=(
        "Return the address associated with the given phone number. "
        "If the phone number is not present in the storage, a 404 error is returned."
    ),
)
async def get_phone_address(
    phone: str = Path(..., description="Phone number to look up."),
    service: PhoneAddressService = Depends(get_phone_address_service),
) -> PhoneAddressRead:
    """Retrieve an address for the specified phone number.

    Args:
        phone: Phone number whose address should be retrieved.
        service: Business-logic service used to access storage.

    Raises:
        HTTPException: With status 404 if phone is not found.

    Returns:
        PhoneAddressRead: Model containing phone number and its address.
    """

    result = await service.get(phone)
    if result is None:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Phone number not found.",
        )
    return result


@router.post(
    "",
    response_model=PhoneAddressRead,
    status_code=HTTPStatus.CREATED,
    responses={
        HTTPStatus.CONFLICT.value: {
            "model": ErrorResponse,
            "description": "Phone number already exists and cannot be created again.",
        },
    },
    summary="Create new phone-address record",
    description=(
        "Create a new binding between phone number and address. "
        "If the phone number already exists, the endpoint returns 409 Conflict."
    ),
)
async def create_phone_address(
    payload: PhoneAddressCreate,
    service: PhoneAddressService = Depends(get_phone_address_service),
) -> PhoneAddressRead:
    """Create a new phone-address record.

    Args:
        payload: Validated request body with ``phone`` and ``address`` fields.
        service: Business-logic service used to access storage.

    Raises:
        HTTPException: With status 409 if the phone number already exists.

    Returns:
        PhoneAddressRead: Model containing the newly created record.
    """

    created = await service.create(payload)
    if not created:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Phone number already exists.",
        )
    return PhoneAddressRead(phone=payload.phone, address=payload.address)


@router.put(
    "/{phone}",
    response_model=PhoneAddressRead,
    responses={
        HTTPStatus.NOT_FOUND.value: {
            "model": ErrorResponse,
            "description": "Phone number not found; nothing to update.",
        },
    },
    summary="Update existing phone-address record",
    description=(
        "Update the address associated with the specified phone number. "
        "If the phone number does not exist, the endpoint returns 404 Not Found."
    ),
)
async def update_phone_address(
    payload: PhoneAddressUpdate,
    phone: str = Path(..., description="Phone number whose address should be updated."),
    service: PhoneAddressService = Depends(get_phone_address_service),
) -> PhoneAddressRead:
    """Update an address for the given phone number.

    Args:
        payload: Request body containing the new address value.
        phone: Phone number whose address must be updated.
        service: Business-logic service used to access storage.

    Raises:
        HTTPException: With status 404 if the phone number does not exist.

    Returns:
        PhoneAddressRead: Model containing the updated record.
    """

    updated = await service.update(phone=phone, address=payload.address)
    if not updated:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Phone number not found.",
        )
    return PhoneAddressRead(phone=phone, address=payload.address)


@router.delete(
    "/{phone}",
    status_code=HTTPStatus.NO_CONTENT,
    responses={
        HTTPStatus.NOT_FOUND.value: {
            "model": ErrorResponse,
            "description": "Phone number not found; nothing to delete.",
        },
        HTTPStatus.NO_CONTENT.value: {
            "description": "Record was successfully deleted.",
        },
    },
    summary="Delete phone-address record",
    description=(
        "Delete a phone-address record from the storage. "
        "If the phone number is absent, the endpoint returns 404 Not Found."
    ),
)
async def delete_phone_address(
    phone: str = Path(..., description="Phone number whose record should be deleted."),
    service: PhoneAddressService = Depends(get_phone_address_service),
) -> None:
    """Delete phone-address record by phone number.

    Args:
        phone: Phone number whose record should be removed.
        service: Business-logic service used to access storage.

    Raises:
        HTTPException: With status 404 if the phone number does not exist.

    Returns:
        None: The endpoint returns empty body with HTTP 204 status on success.
    """

    deleted = await service.delete(phone=phone)
    if not deleted:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Phone number not found.",
        )
