"""
GenAI Interpreter Service
-------------------------
Orchestrates multi-agent workflows to interpret VIN predictive data
and generate standardized summaries and recommendations.
"""

from app.agents.vin_explainer_agent import VinExplainerAgent
from app.models.vin import VinResponse

class GenAIInterpreterService:
    """
    GenAI Interpreter Service

    This service acts as the orchestrator for VIN-level predictive interpretation.
    It utilizes agent classes to produce natural-language summaries and operational action packs.
    """
    def __init__(self):
        """
        Initialize interpreter service with required agents and resources.
        """
        self.agent = VinExplainerAgent()

    def interpret_vin(self, vin: str) -> VinResponse:
        """
        Run the full interpretation workflow for a given VIN.

        Args:
            vin (str): Vehicle Identification Number to analyze.

        Returns:
            VinResponse: The complete response including summary and recommended actions.
        """
        summary = self.agent.explain(vin)
        action_pack = self.agent.recommend_action(vin)
        response = VinResponse(
            vin=vin,
            summary=summary,
            action_pack=action_pack
        )
        return response
