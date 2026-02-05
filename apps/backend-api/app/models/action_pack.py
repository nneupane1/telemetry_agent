"""
Action Pack domain models.

This module defines the canonical structure for Action Packs:
the final, human-consumable artifacts produced by the platform
and delivered via PDF or email.

Used by:
- PDF exporter
- Email delivery service
- Approval workflows
- Audit and traceability pipelines
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.vin import Recommendation


# ---------------------------------------------------------------------
# Approval Metadata
# ---------------------------------------------------------------------

class ApprovalMetadata(BaseModel):
    """
    Captures approval and sign-off information for an Action Pack.
    """

    status: str = Field(
        ...,
        description="Approval status",
        example="APPROVED",
    )
    approved_by: Optional[str] = Field(
        None,
        description="Identifier of approving user or role",
        example="control_room_operator",
    )
    approved_at: Optional[datetime] = Field(
        None,
        description="Timestamp of approval",
    )
    notes: Optional[str] = Field(
        None,
        description="Optional approval notes or comments",
    )

    class Config:
        frozen = True


# ---------------------------------------------------------------------
# Action Pack (Root Model)
# ---------------------------------------------------------------------

class ActionPack(BaseModel):
    """
    Final, auditable Action Pack delivered to stakeholders.

    This object is the authoritative representation of:
    - what was detected
    - why it matters
    - what should be done
    """

    action_pack_id: str = Field(
        ...,
        description="Unique Action Pack identifier",
        example="AP-2024-09-000123",
    )

    subject_type: str = Field(
        ...,
        description="Scope of the Action Pack",
        example="VIN",  # or COHORT
    )

    subject_id: str = Field(
        ...,
        description="VIN or cohort identifier",
        example="WVWZZZ1KZ6W000001",
    )

    title: str = Field(
        ...,
        description="Action Pack title",
        example="Elevated fuel system risk detected",
    )

    executive_summary: str = Field(
        ...,
        description="Concise summary for decision-makers",
    )

    recommendations: List[Recommendation] = Field(
        default_factory=list,
        description="Actionable recommendations included in this pack",
    )

    approval: Optional[ApprovalMetadata] = Field(
        None,
        description="Approval and sign-off metadata",
    )

    generated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the Action Pack was generated",
    )

    model_version: str = Field(
        ...,
        description="Version of the Action Pack generation logic",
        example="v1.0.0",
    )

    class Config:
        frozen = True
        schema_extra = {
            "example": {
                "action_pack_id": "AP-2024-09-000123",
                "subject_type": "VIN",
                "subject_id": "WVWZZZ1KZ6W000001",
                "title": "Elevated fuel system risk detected",
                "executive_summary": "Recurring fuel pressure anomalies indicate elevated failure risk within the next service window.",
                "model_version": "v1.0.0",
            }
        }
