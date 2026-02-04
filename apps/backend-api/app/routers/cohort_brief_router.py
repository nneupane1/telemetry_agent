"""
Cohort Brief Router
-------------------
Exposes API endpoints for cohort-level predictive summaries and trends
using the CohortBriefInterpreterService.
"""

from fastapi import APIRouter
from typing import List, Dict
from pydantic import BaseModel, Field
from app.services.cohort_brief_interpreter import CohortBriefInterpreterService

class CohortRequest(BaseModel):
    """
    Request payload for cohort brief and trends analysis.
    """
    vin_data: List[Dict] = Field(..., description="List of dictionaries with VIN and predictive outputs (including risk_level).")

class CohortSummaryResponse(BaseModel):
    """
    Response containing a narrative summary for the cohort.
    """
    summary: str = Field(..., description="Narrative brief for the entire cohort.")

class CohortRiskTrendsResponse(BaseModel):
    """
    Response containing cohort risk level counts.
    """
    trends: Dict[str, int] = Field(..., description="Counts of risk levels across cohort.")

class CohortBriefRouter:
    """
    Handles all cohort-level endpoints.
    """
    def __init__(self):
        self.router = APIRouter()
        self.service = CohortBriefInterpreterService()
        self.router.add_api_route(
            "/summary",
            self.get_cohort_summary,
            methods=["POST"],
            response_model=CohortSummaryResponse,
            summary="Get a narrative brief of cohort predictive anomalies and actions."
        )
        self.router.add_api_route(
            "/trends",
            self.get_cohort_trends,
            methods=["POST"],
            response_model=CohortRiskTrendsResponse,
            summary="Get risk level breakdown for a cohort."
        )

    def get_cohort_summary(self, request: CohortRequest) -> CohortSummaryResponse:
        """
        POST /cohort/summary
        Returns a narrative brief for the entire cohort.

        Args:
            request (CohortRequest): The cohort VIN data.

        Returns:
            CohortSummaryResponse: Narrative summary.
        """
        summary = self.service.generate_cohort_summary(request.vin_data)
        return CohortSummaryResponse(summary=summary)

    def get_cohort_trends(self, request: CohortRequest) -> CohortRiskTrendsResponse:
        """
        POST /cohort/trends
        Returns a risk level breakdown for the cohort.

        Args:
            request (CohortRequest): The cohort VIN data.

        Returns:
            CohortRiskTrendsResponse: Risk counts.
        """
        trends = self.service.get_risk_trends(request.vin_data)
        return CohortRiskTrendsResponse(trends=trends)
