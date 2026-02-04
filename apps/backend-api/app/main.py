"""
Main Application Entry Point
---------------------------
Creates and configures the FastAPI app, including router registration.
"""

from fastapi import FastAPI
from app.routers.vin import VinRouter

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
    # Register VIN endpoints using the OOP router
    app.include_router(
        VinRouter().router, 
        prefix="/vin", 
        tags=["VIN"]
    )
    return app

# Application instance for ASGI servers
app = create_app()
