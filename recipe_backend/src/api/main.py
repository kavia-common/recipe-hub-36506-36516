from typing import List, Optional

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.db.session import Base, engine
from dotenv import load_dotenv

# Load environment variables (CORS settings, etc.)
load_dotenv()

API_TITLE = "Recipe Hub API"
API_DESCRIPTION = (
    "Backend for the Recipe Hub application that allows users to discover, create, "
    "and manage recipes."
)
API_VERSION = "0.1.0"

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    openapi_tags=[
        {"name": "Health", "description": "Service health and metadata."},
        {"name": "Info", "description": "General information and usage notes."},
    ],
)

# Configure CORS from env, fallback to wildcard for initial setup
cors_origins_env: Optional[str] = os.getenv("CORS_ORIGINS")
allow_origins: List[str] = ["*"]
if cors_origins_env:
    allow_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    """
    Create database tables on startup.

    Note: In a production environment, migrations via Alembic are recommended.
    """
    Base.metadata.create_all(bind=engine)


# PUBLIC_INTERFACE
@app.get("/", tags=["Health"], summary="Health Check", description="Simple health check endpoint.")
def health_check():
    """Health check endpoint returning a simple status message."""
    return {"message": "Healthy"}


# PUBLIC_INTERFACE
@app.get(
    "/ws-info",
    tags=["Info"],
    summary="WebSocket Usage",
    description=(
        "This project currently does not expose a WebSocket endpoint. "
        "Future real-time features would document connection details here."
    ),
    operation_id="websocket_usage_info",
)
def websocket_info():
    """Describe WebSocket usage for API docs (placeholder)."""
    return {"websocket": "No active WebSocket endpoints yet."}
