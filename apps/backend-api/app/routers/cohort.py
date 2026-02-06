"""
Cohort API Router.

Exposes cohort-level interpretation endpoints.
Thin HTTP layer over the GenAI interpreter.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.models.cohort import CohortInterpretation, CohortListResponse
from app.services.genai_interpreter import GenAIInterpreter
from app.utils.logger import get_logger, log_event

router = APIRouter(prefix="/cohort", tags=["cohort"])
logger = get_logger(__name__)


# ---------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------

def get_interpreter() -> GenAIInterpreter:
    return GenAIInterpreter(model_version="v1.0.0")


# ---------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------

@router.get(
    "/list",
    response_model=CohortListResponse,
    status_code=status.HTTP_200_OK,
)
def list_cohorts(
    x_request_id: str | None = Header(default=None),
    interpreter: GenAIInterpreter = Depends(get_interpreter),
) -> CohortListResponse:
    """
    List available cohort IDs for dashboard selectors.
    """

    log_event(
        logger,
        "Cohort list API request received",
    )

    try:
        _ = x_request_id  # reserved for future request tracing
        cohorts = interpreter.list_cohorts()
        return CohortListResponse(cohorts=cohorts)
    except Exception as exc:
        log_event(
            logger,
            "Cohort list request failed",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load cohort list",
        ) from exc


@router.get(
    "/{cohort_id}",
    response_model=CohortInterpretation,
    status_code=status.HTTP_200_OK,
)
def interpret_cohort(
    cohort_id: str,
    x_request_id: str | None = Header(default=None),
    interpreter: GenAIInterpreter = Depends(get_interpreter),
) -> CohortInterpretation:
    """
    Generate a cohort-level predictive interpretation.
    """

    log_event(
        logger,
        "Cohort API request received",
        extra={"cohort_id": cohort_id},
    )

    try:
        interpretation = interpreter.interpret_cohort(
            cohort_id=cohort_id,
            request_id=x_request_id,
        )
        return interpretation

    except Exception as exc:
        log_event(
            logger,
            "Cohort interpretation failed",
            extra={"cohort_id": cohort_id},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate cohort interpretation",
        ) from exc
