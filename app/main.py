"""
Application entry point.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.logger import logger

from app.db.database import (
    startup_database,
    shutdown_database,
)

from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    UserAlreadyExistsError,
    InvalidCredentialsError,
    InactiveUserError,
    UserNotFoundError,
)

from app.api.v1.auth import router as auth_router
from app.api.v1.bookings import router as booking_router
from app.api.v1.services import router as service_router
from app.api.v1.vehicles import router as vehicle_router
from app.api.v1.car_brands import router as car_brand_router
from app.api.v1.car_models import router as car_model_router
from app.api.v1.admin import router as admin_router
from app.api.v1.admin_booking import router as admin_booking_router
from app.api.v1.admin_customer import (router as admin_customer_router)
from app.api.v1.availability import (router as availability_router)
from app.api.v1.payments import router as payment_router
from app.api.v1.webhook import router as webhook_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Car Wash Backend...")

    await startup_database()

    yield

    logger.info("Shutting down Car Wash Backend...")

    await shutdown_database()


app = FastAPI(
    title="Car Wash API",
    description="Backend API for the Car Wash Booking Platform.",
    version="2.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------
# Exception Handlers
# ---------------------------------------------------------

@app.exception_handler(AuthenticationError)
async def authentication_handler(request: Request, exc: AuthenticationError):
    return JSONResponse(
        status_code=401,
        content={"detail": str(exc)},
    )

@app.exception_handler(AuthorizationError)
async def authorization_handler(
    request: Request,
    exc: AuthorizationError,
):
    return JSONResponse(
        status_code=403,
        content={"detail": str(exc)},
    )

@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(request: Request, exc: UserNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )

@app.exception_handler(UserAlreadyExistsError)
async def user_exists_handler(
    request: Request,
    exc: UserAlreadyExistsError,
):
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)},
    )


@app.exception_handler(InvalidCredentialsError)
async def invalid_credentials_handler(
    request: Request,
    exc: InvalidCredentialsError,
):
    return JSONResponse(
        status_code=401,
        content={"detail": str(exc)},
    )


@app.exception_handler(InactiveUserError)
async def inactive_user_handler(
    request: Request,
    exc: InactiveUserError,
):
    return JSONResponse(
        status_code=403,
        content={"detail": str(exc)},
    )


# ---------------------------------------------------------
# Routers
# ---------------------------------------------------------

app.include_router(auth_router, prefix="/api/v1")
app.include_router(booking_router, prefix="/api/v1")
app.include_router(service_router, prefix="/api/v1")
app.include_router(car_brand_router, prefix="/api/v1")
app.include_router(car_model_router, prefix="/api/v1")
app.include_router(vehicle_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(admin_booking_router, prefix="/api/v1")
app.include_router(admin_customer_router, prefix="/api/v1")
app.include_router(availability_router, prefix="/api/v1")
app.include_router(payment_router, prefix="/api/v1")
app.include_router(webhook_router, prefix="/api/v1")

# ---------------------------------------------------------
# Health Endpoints
# ---------------------------------------------------------

@app.get("/", tags=["Health"])
async def root():
    return {
        "message": "Car Wash API is running 🚀",
        "status": "online",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {
        "status": "healthy",
    }