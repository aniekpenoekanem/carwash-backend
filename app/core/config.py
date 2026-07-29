"""
Application configuration.

Loads settings from environment variables (.env) and provides a
single Settings instance for the entire application.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # -----------------------------------------------------
    # Application
    # -----------------------------------------------------

    APP_NAME: str = "Car Wash Backend"

    APP_VERSION: str = "2.0.0"

    DEBUG: bool = True

    API_PREFIX: str = "/api/v1"

    # -----------------------------------------------------
    # Database
    # -----------------------------------------------------

    DATABASE_URL: str = Field(
        default=f"sqlite+aiosqlite:///{BASE_DIR}/carwash.db",
    )

    # -----------------------------------------------------
    # Paystack
    # -----------------------------------------------------

    PAYSTACK_SECRET_KEY: str

    PAYSTACK_PUBLIC_KEY: str = ""

    PAYSTACK_BASE_URL: str = "https://api.paystack.co"

    PAYMENT_TIMEOUT_MINUTES: int = 15

    # -----------------------------------------------------
    # Security
    # -----------------------------------------------------

    SECRET_KEY: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    ALGORITHM: str = "HS256"

    # -----------------------------------------------------
    # CORS
    # -----------------------------------------------------

    ALLOWED_ORIGINS: list[str] = [
        "*"
    ]


@lru_cache
def get_settings() -> Settings:
    """
    Return a cached Settings instance.
    """
    return Settings()


settings = get_settings()