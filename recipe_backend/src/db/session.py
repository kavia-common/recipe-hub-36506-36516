from __future__ import annotations

import os
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Read DATABASE_URL from environment; do not hardcode defaults
DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Provide a clear error message to guide environment setup
    raise RuntimeError(
        "DATABASE_URL environment variable is not set. "
        "Please define it in your environment or in a .env file. "
        "See .env.example for the required variables."
    )

# Create SQLAlchemy engine
# pool_pre_ping=True to avoid stale connections
engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)

# Configure session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session, future=True)

# Base declarative class for models to inherit
Base = declarative_base()


# PUBLIC_INTERFACE
def get_db() -> Generator[Session, None, None]:
    """Dependency that yields a database session and ensures it is properly closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
