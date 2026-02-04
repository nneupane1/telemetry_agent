"""
Cohort Brief Interpreter Service
-------------------------------
Orchestrates the generation of fleet-level predictive anomaly summaries
and risk distribution using the CohortBriefAgent.
"""

from typing import List, Dict
from app.agents.cohort_brief_agent import CohortBriefAgent

class CohortBriefInterpreterService:
    """
    CohortBriefInterpreterService

    Provides APIs to summarize cohort-level predictive maintenance risks and operational recommendations.
    """
    def __init__(self):
        """
        Initialize the service with a cohort brief agent.
        """
        self.agent = CohortBriefAgent()

    def generate_cohort_summary(self, vin_data: List[Dict]) -> str:
        """
        Produces a narrative summary of cohort anomalies and actions.

        Args:
            vin_data (List[Dict]): List of VIN predictive outputs.

        Returns:
            str: Cohort-level narrative brief.
        """
        return self.agent.generate_brief(vin_data)

    def get_risk_trends(self, vin_data: List[Dict]) -> Dict[str, int]:
        """
        Returns risk level breakdown for the cohort.

        Args:
            vin_data (List[Dict]): List of VIN predictive outputs.

        Returns:
            Dict[str, int]: Counts of each risk level.
        """
        return self.agent.summarize_trends(vin_data)
