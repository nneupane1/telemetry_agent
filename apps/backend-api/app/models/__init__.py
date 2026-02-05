"""
Domain models package.

This package contains all canonical Pydantic models representing
the structured outputs and inputs of the GenAI Predictive Interpreter Platform.
"""

from app.models.vin import (
    VinInterpretation,
    Recommendation,
    EvidenceItem,
)
from app.models.cohort import (
    CohortInterpretation,
    CohortMetric,
    CohortAnomaly,
)
from app.models.action_pack import (
    ActionPack,
    ApprovalMetadata,
)

__all__ = [
    # VIN
    "VinInterpretation",
    "Recommendation",
    "EvidenceItem",
    # Cohort
    "CohortInterpretation",
    "CohortMetric",
    "CohortAnomaly",
    # Action Pack
    "ActionPack",
    "ApprovalMetadata",
]
