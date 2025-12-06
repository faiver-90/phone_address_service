"""
Pydantic schemas for phone-address operations.

These schemas define the data contracts for all API endpoints and are used
both for validation and automatic documentation generation (OpenAPI/Swagger).
"""

from pydantic import BaseModel, Field


class PhoneAddressBase(BaseModel):
    """Base model for phone-address data shared by multiple operations."""

    address: str = Field(
        ...,
        description="Physical address associated with the phone number.",
        examples=["Moscow, Tverskaya street, 1"],
        min_length=1,
        max_length=1024,
    )


class PhoneAddressCreate(PhoneAddressBase):
    """Model for creating a new phone-address record."""

    phone: str = Field(
        ...,
        description=(
            "Phone number used as a unique key in the storage. "
            "Format is not strictly validated and may contain symbols like '+', "
            "spaces or dashes, but should be unique within the system."
        ),
        examples=["+7 999 123-45-67"],
        min_length=3,
        max_length=64,
    )


class PhoneAddressUpdate(PhoneAddressBase):
    """Model for updating an existing phone-address record.

    Only the address field is allowed to be changed.
    """


class PhoneAddressRead(PhoneAddressBase):
    """Model returned by API when reading phone-address data."""

    phone: str = Field(
        ...,
        description="Phone number associated with the address.",
        examples=["+7 999 123-45-67"],
    )


class ErrorResponse(BaseModel):
    """Generic error response model.

    Attributes:
        detail: Human-readable error description.
    """

    detail: str = Field(..., description="Error message describing the problem.")
