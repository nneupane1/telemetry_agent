"""
VIN domain models.

This module defines the canonical data contract for all VIN-level
predictive interpretations produced by the platform.

Used by:
- GenAI agents
- API responses
- PDF reports
- Evidence & audit workflows
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator


# ---------------------------------------------------------------------
# Evidence Models
# ---------------------------------------------------------------------

class EvidenceItem(BaseModel):
    """
    Atomic piece of evidence contributing to a recommendation.
    """

    source_model: str = Field(
        ...,
        description="Originating model (MH, MP, FIM, etc.)",
        example="MH",
    )
    signal_code: str = Field(
        ...,
        description="Raw signal or HI code",
        example="HI-4302",
    )
    signal_description: str = Field(
        ...,
        description="Human-readable explanation of the signal",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Model confidence score (0–1)",
    )
    observed_at: datetime = Field(
        ...,
        description="Timestamp when the signal was observed",
    )

    class Config:
        frozen = True


# ---------------------------------------------------------------------
# Recommendation Model
# ---------------------------------------------------------------------

class Recommendation(BaseModel):
    """
    Actionable recommendation generated for a VIN.
    """

    title: str = Field(
        ...,
        description="Short recommendation headline",
        example="Inspect high-pressure fuel pump",
    )
    rationale: str = Field(
        ...,
        description="Clear, natural-language justification",
    )
    urgency: str = Field(
        ...,
        description="Urgency level",
        example="HIGH",
    )
    suggested_action: str = Field(
        ...,
        description="Concrete next step for operators or maintenance",
    )
    evidence: List[EvidenceItem]

    class Config:
        frozen = True


# ---------------------------------------------------------------------
# VIN Interpretation (Root Model)
# ---------------------------------------------------------------------

class VinInterpretation(BaseModel):
    """
    Final, auditable VIN-level interpretation output.

    This is the primary artifact produced by the GenAI layer.
    """

    vin: str = Field(
        ...,
        min_length=5,
        max_length=32,
        description="Vehicle Identification Number",
    )

    summary: str = Field(
        ...,
        description="High-level natural-language summary for this VIN",
    )

    health_index: Optional[float] = Field(
        None,
        ge=0.0,
        le=100.0,
        description="Aggregated health index (0–100), if available",
    )

    risk_level: str = Field(
        ...,
        description="Overall assessed risk level",
        example="ELEVATED",
    )

    recommendations: List[Recommendation] = Field(
        default_factory=list,
        description="Ordered list of actionable recommendations",
    )

    evidence_summary: Optional[Dict[str, Dict[str, object]]] = Field(
        None,
        description="Consolidated evidence grouped by model and signal code",
    )

    generated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when interpretation was generated",
    )

    model_version: str = Field(
        ...,
        description="Version of the interpretation logic / prompt set",
        example="v1.0.0",
    )

    @validator("vin")
    def normalize_vin(cls, v: str) -> str:
        return v.strip().upper()

    class Config:
        frozen = True
        schema_extra = {
            "example": {
                "vin": "WVWZZZ1KZ6W000001",
                "summary": "Elevated risk detected due to recurring fuel system anomalies.",
                "health_index": 62.4,
                "risk_level": "ELEVATED",
                "model_version": "v1.0.0",
                "recommendations": [],
            }
        }
