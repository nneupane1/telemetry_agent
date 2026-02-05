"""
Approval Router.

Handles operator approval decisions for VINs and cohorts.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

from app.services.approval_store import ApprovalStore

router = APIRouter(prefix="/approval", tags=["approval"])

store = ApprovalStore()


# ------------------------------------------------------------
# Request / Response models
# ------------------------------------------------------------

class ApprovalRequest(BaseModel):
    """
    Incoming approval decision.
    """
    subject_type: str = Field(..., description="vin or cohort")
    subject_id: str = Field(..., description="VIN or cohort identifier")
    decision: str = Field(..., description="approve | reject | escalate")
    comment: str = Field("", description="Operator comment")
    decided_by: Optional[str] = Field(None, description="Operator identifier")


class ApprovalRecord(BaseModel):
    subject_type: str
    subject_id: str
    decision: str
    comment: str
    decided_by: str
    timestamp: str


# ------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------

@router.post("", response_model=ApprovalRecord)
def record_approval(request: ApprovalRequest) -> ApprovalRecord:
    """
    POST /approval

    Record an approval decision.
    """

    decision = request.decision.lower()
    if decision not in {"approve", "reject", "escalate"}:
        raise HTTPException(
            status_code=400,
            detail="decision must be approve, reject, or escalate",
        )

    record = store.record_decision(
        subject_type=request.subject_type,
        subject_id=request.subject_id,
        decision=decision,
        comment=request.comment,
        decided_by=request.decided_by,
    )

    return ApprovalRecord(**record)


@router.get("", response_model=List[ApprovalRecord])
def list_approvals(
    subject_type: Optional[str] = None,
    subject_id: Optional[str] = None,
) -> List[ApprovalRecord]:
    """
    GET /approval

    List approval decisions with optional filtering.
    """

    records = store.list_decisions(
        subject_type=subject_type,
        subject_id=subject_id,
    )

    return [ApprovalRecord(**r) for r in records]
