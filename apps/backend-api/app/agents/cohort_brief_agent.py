"""
Cohort Brief Agent
------------------
Generates fleet-level (cohort) predictive anomaly summaries and operational briefings.
"""

from typing import List, Dict

class CohortBriefAgent:
    """
    CohortBriefAgent

    Responsible for aggregating predictive signals from multiple VINs,
    analyzing fleet trends, and generating actionable cohort-level briefs.
    """
    def __init__(self):
        """
        Initialize the agent.
        In a production system, this might include loading
        reference dictionaries, confidence thresholds, and ML models.
        """
        pass

    def generate_brief(self, vin_data: List[Dict]) -> str:
        """
        Create a fleet-wide summary brief highlighting predictive anomalies and trends.

        Args:
            vin_data (List[Dict]): List of VIN predictive outputs, one per vehicle.

        Returns:
            str: Cohort-level anomaly summary and recommended operational action.
        """
        high_risk_vins = [vin["vin"] for vin in vin_data if vin.get("risk_level") == "high"]
        moderate_risk_vins = [vin["vin"] for vin in vin_data if vin.get("risk_level") == "moderate"]
        n_total = len(vin_data)
        n_high = len(high_risk_vins)
        n_mod = len(moderate_risk_vins)

        brief = (
            f"Cohort analysis for {n_total} vehicles:\n"
            f"- {n_high} vehicles flagged as HIGH risk ({', '.join(high_risk_vins)})\n"
            f"- {n_mod} vehicles flagged as MODERATE risk ({', '.join(moderate_risk_vins)})\n"
            "Recommended action: Prioritize review for all high-risk VINs and schedule follow-up for moderate-risk group."
        )
        return brief

    def summarize_trends(self, vin_data: List[Dict]) -> Dict[str, int]:
        """
        Produces a simple breakdown of risk distribution.

        Args:
            vin_data (List[Dict]): List of VIN predictive outputs.

        Returns:
            Dict[str, int]: Counts of risk levels in the cohort.
        """
        risk_counts = {"high": 0, "moderate": 0, "low": 0}
        for vin_info in vin_data:
            risk = vin_info.get("risk_level", "low")
            if risk in risk_counts:
                risk_counts[risk] += 1
        return risk_counts
