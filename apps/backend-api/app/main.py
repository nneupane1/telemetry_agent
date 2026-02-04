"""
Main Application Entry Point
---------------------------
Creates and configures the FastAPI app, including router registration for
VIN interpretation and cohort brief endpoints.
"""

from fastapi import FastAPI
from app.routers.vin import VinRouter
from app.routers.cohort_brief_router import CohortBriefRouter

def create_app() -> FastAPI:
    """
    Factory function to initialize and configure the FastAPI app.
    
    Returns:
        FastAPI: The configured FastAPI application instance.
    """
    app = FastAPI(
        title="GenAI Predictive Interpreter API",
        description="Multi-agent GenAI backend for predictive vehicle maintenance.",
        version="1.0.0"
    )
    # Register VIN endpoints
    app.include_router(
        VinRouter().router, 
        prefix="/vin", 
        tags=["VIN"]
    )
    # Register Cohort Brief endpoints
    app.include_router(
        CohortBriefRouter().router,
        prefix="/cohort",
        tags=["Cohort"]
    )
    return app

# Application instance for ASGI servers
app = create_app()
