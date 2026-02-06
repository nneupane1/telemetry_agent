"""
VIN API Router.

Exposes VIN-level interpretation endpoints.
Thin HTTP layer over the GenAI interpreter.
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.models.vin import VinInterpretation
from app.services.genai_interpreter import GenAIInterpreter
from app.services.reference_loader import ReferenceLoader
from app.utils.logger import get_logger, log_event

router = APIRouter(prefix="/vin", tags=["vin"])
logger = get_logger(__name__)
reference_loader = ReferenceLoader()


# ---------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------

def get_interpreter() -> GenAIInterpreter:
    return GenAIInterpreter(model_version="v1.0.0")


def load_reference_map() -> Dict[str, Dict[str, Any]]:
    """
    Load merged semantic reference dictionary.
    """
    try:
        return reference_loader.load_reference_map()
    except Exception:
        log_event(
            logger,
            "Reference map load failed, using empty map fallback",
        )
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
