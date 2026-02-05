"""
API router package.

This package contains all FastAPI routers that expose the
public HTTP interface of the service.
"""

from app.routers.vin import router as vin_router
from app.routers.cohort import router as cohort_router
from app.routers.action_pack import router as action_pack_router

__all__ = [
    "vin_router",
    "cohort_router",
    "action_pack_router",
]
