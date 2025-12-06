"""
Entry point for the Phone Address Service application.

The module defines the FastAPI application, configures metadata for
automatic documentation (Swagger / OpenAPI) and registers all API routers.
"""

from fastapi import Depends, FastAPI
from redis.asyncio import Redis

from app.api.v1.deps import get_redis_client
from app.api.v1.routes_phone_address import router as phone_address_router
from app.core.config import get_settings
from app.core.redis import lifespan

settings = get_settings()

description = """
Service for storing and managing "phone - address" pairs.

The API is built on top of FastAPI and uses Redis as a fast key-value
storage. It can be used for:

* Caching frequently requested user addresses
* Quick access to delivery addresses by phone number
* Temporary storage for phone-address bindings
"""

app = FastAPI(
    title=settings.project_name,
    description=description,
    version="1.0.0",
    contact={
        "name": "Phone Address Service",
        "url": "https://example.com",
    },
    lifespan=lifespan,
    swagger_ui_parameters={"defaultModelsExpandDepth": 1},
)

app.include_router(phone_address_router, prefix=settings.api_v1_prefix)


@app.get(
    "/health",
    tags=["Service"],
    summary="Health check",
    description="Simple endpoint for checking that the service is alive.",
)
async def healthcheck(redis: Redis = Depends(get_redis_client)) -> dict[str, str]:
    """Return service health status.

    This endpoint can be used by monitoring systems or orchestrators to
    verify that the application is running.

    Returns:
        dict[str, str]: A dictionary with a single ``status`` field.
    """
    try:
        pong = await redis.ping()
        redis_status = "ok" if pong else "unavailable"
    except Exception:
        redis_status = "unavailable"

    overall = "ok" if redis_status == "ok" else "degraded"

    return {
        "status": overall,
        "redis": redis_status,
    }
