from __future__ import annotations

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()


class Settings(BaseModel):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = Field(..., description="SQLAlchemy database URL")

    # Security/JWT
    JWT_SECRET: str = Field(..., description="Secret key for signing JWT tokens")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        60, description="Access token expiration time in minutes"
    )

    # CORS
    CORS_ORIGINS: Optional[str] = Field(
        None,
        description="Comma-separated list of allowed CORS origins. If not set, '*' is allowed.",
    )

    # Site URL (useful for email redirects in other integrations)
    SITE_URL: Optional[str] = Field(
        None, description="Public site URL used for redirects (optional)"
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Load and cache application settings from environment variables.

    Raises:
        ValueError: If required environment variables are missing.
    """
    env = {
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "JWT_SECRET": os.getenv("JWT_SECRET"),
        "ACCESS_TOKEN_EXPIRE_MINUTES": int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
        ),
        "CORS_ORIGINS": os.getenv("CORS_ORIGINS"),
        "SITE_URL": os.getenv("SITE_URL"),
    }
    # Validate presence of critical vars
    missing = [k for k in ("DATABASE_URL", "JWT_SECRET") if not env.get(k)]
    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}. "
            "Please define them in your environment or .env file."
        )
    return Settings(**env)


def get_cors_origins(settings: Settings) -> List[str]:
    """
    Convert the CORS_ORIGINS setting into a list of allowed origins.
    Defaults to wildcard if not specified.
    """
    if not settings.CORS_ORIGINS:
        return ["*"]
    return [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
