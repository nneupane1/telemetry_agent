"""
VIN API Router.

Exposes VIN-level interpretation endpoints.
Thin HTTP layer over the GenAI interpreter.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.models.vin import VinInterpretation
from app.services.genai_interpreter import GenAIInterpreter
from app.utils.config import load_config
from app.utils.logger import get_logger, log_event

router = APIRouter(prefix="/vin", tags=["vin"])
logger = get_logger(__name__)


# ---------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------

def get_interpreter() -> GenAIInterpreter:
    return GenAIInterpreter(model_version="v1.0.0")


def load_reference_map() -> dict:
    """
    Placeholder for reference dictionary loading.
    In production this may load from file, cache, or DB.
    """
    return {}


# ---------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------

@router.get(
    "/{vin}",
    response_model=VinInterpretation,
    status_code=status.HTTP_200_OK,
)
def interpret_vin(
    vin: str,
    x_request_id: str | None = Header(default=None),
    interpreter: GenAIInterpreter = Depends(get_interpreter),
) -> VinInterpretation:
    """
    Generate a VIN-level predictive interpretation.
    """

    log_event(
        logger,
        "VIN API request received",
        extra={"vin": vin},
    )

    try:
        interpretation = interpreter.interpret_vin(
            vin=vin,
            reference_map=load_reference_map(),
            request_id=x_request_id,
        )
        return interpretation

    except Exception as exc:
        log_event(
            logger,
            "VIN interpretation failed",
            extra={"vin": vin},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate VIN interpretation",
        ) from exc
