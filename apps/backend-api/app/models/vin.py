"""
VIN-level domain models.
Authoritative schema for GenAI interpretation, APIs, and evidence trails.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, conint, confloat


class HealthIndicator(BaseModel):
    """
    Single health indicator signal (MH / MP / FIM).
    """

    code: str = Field(..., description="Canonical HI code (e.g. HI-4302)")
    family: str = Field(..., description="HI family or subsystem")
    score: confloat(ge=0.0, le=1.0)
    confidence: confloat(ge=0.0, le=1.0)
    severity: conint(ge=0, le=5)
    description: Optional[str] = None

    class Config:
        frozen = True


class VinSnapshot(BaseModel):
    """
    Point-in-time VIN snapshot used by agents.
    """

    vin: str = Field(..., min_length=5)
    timestamp: datetime

    machine_health: List[HealthIndicator]
    maintenance_predictions: List[HealthIndicator]
    failure_impacts: List[HealthIndicator]

    class Config:
        frozen = True


class VinNarrative(BaseModel):
    """
    Final GenAI-generated VIN explanation.
    """

    vin: str
    generated_at: datetime
    summary: str
    key_risks: List[str]
    recommended_actions: List[str]
    evidence_refs: List[str]

    class Config:
        frozen = True
