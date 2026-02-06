"""
Action Pack API Router.

Exposes endpoints for assembling delivery-ready Action Packs
from existing interpretations.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.models.action_pack import ActionPack
from app.models.vin import Recommendation
from app.services.genai_interpreter import GenAIInterpreter
from app.utils.logger import get_logger, log_event

router = APIRouter(prefix="/action-pack", tags=["action-pack"])
logger = get_logger(__name__)


# ---------------------------------------------------------------------
# Request Models
# ---------------------------------------------------------------------

class ActionPackRequest(BaseModel):
    """
    Input payload for Action Pack assembly.
    """

    subject_type: str = Field(..., example="VIN")
    subject_id: str = Field(..., example="WVWZZZ1KZ6W000001")
    title: str
    executive_summary: str
    recommendations: list[Recommendation]


# ---------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------

def get_interpreter() -> GenAIInterpreter:
    return GenAIInterpreter(model_version="v1.0.0")


# ---------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------

@router.post(
    "/",
    response_model=ActionPack,
    status_code=status.HTTP_201_CREATED,
)
def create_action_pack(
    payload: ActionPackRequest,
    interpreter: GenAIInterpreter = Depends(get_interpreter),
) -> ActionPack:
    """
    Assemble a delivery-ready Action Pack.
    """

    log_event(
        logger,
        "Action Pack creation requested",
        extra={
            "subject_type": payload.subject_type,
            "subject_id": payload.subject_id,
        },
    )

    try:
        action_pack = interpreter.build_action_pack(
            subject_type=payload.subject_type.upper(),
            subject_id=payload.subject_id.strip(),
            title=payload.title,
            executive_summary=payload.executive_summary,
            recommendations=payload.recommendations,
        )
        return action_pack

    except Exception as exc:
        log_event(
            logger,
            "Action Pack creation failed",
            extra={"subject_id": payload.subject_id},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create Action Pack",
        ) from exc
