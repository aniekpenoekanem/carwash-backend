"""
Application entry point.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.logger import logger
from app.db.database import startup_database, shutdown_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown.
    """
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


@app.get("/", tags=["Health"])
async def root():
    """
    Root endpoint.
    """
    return {
        "message": "Car Wash API is running 🚀",
        "status": "online",
    }


@app.get("/health", tags=["Health"])
async def health():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
    }