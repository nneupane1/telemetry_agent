"""
Application entrypoint.

Initializes the FastAPI application, registers routers,
and configures lifecycle hooks.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    action_pack,
    approval,
    chat,
    cohort,
    export,
    vin,
)
from app.utils.config import load_config
from app.utils.logger import get_logger, log_event

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """

    try:
        config = load_config()
        env_name = config.env
    except Exception:
        config = None
        env_name = "unconfigured"

    app = FastAPI(
        title="GenAI Predictive Interpreter Platform",
        version="1.0.0",
        description="Automated GenAI interpretation of predictive maintenance signals",
    )

    # -----------------------------------------------------------------
    # Middleware
    # -----------------------------------------------------------------

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # tighten in prod
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -----------------------------------------------------------------
    # Routers
    # -----------------------------------------------------------------

    app.include_router(vin.router)
    app.include_router(cohort.router)
    app.include_router(action_pack.router)
    app.include_router(chat.router)
    app.include_router(export.router)
    app.include_router(approval.router)

    # -----------------------------------------------------------------
    # Lifecycle hooks
    # -----------------------------------------------------------------

    @app.get("/health", tags=["ops"])
    def health() -> dict:
        return {"status": "ok", "service": "genai-predictive-backend"}

    @app.on_event("startup")
    def on_startup() -> None:
        log_event(
            logger,
            "Application startup",
            extra={"env": env_name},
        )

    @app.on_event("shutdown")
    def on_shutdown() -> None:
        log_event(
            logger,
            "Application shutdown",
        )

    return app


app = create_app()
