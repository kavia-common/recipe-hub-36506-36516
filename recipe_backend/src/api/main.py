from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import get_cors_origins, get_settings
from src.db.session import Base, engine
from src.api.routers_auth import router as auth_router
from src.api.routers_recipes import router as recipes_router

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
        {"name": "Auth", "description": "User registration, login, and profile endpoints."},
        {"name": "Recipes", "description": "Endpoints to manage recipes."},
    ],
)

# Configure CORS from env using config
settings = get_settings()
allow_origins: List[str] = get_cors_origins(settings)

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


# Include routers
app.include_router(auth_router)
app.include_router(recipes_router)
