
"""
VIN Router
----------
Exposes API endpoints for VIN predictive interpretation,
using clean object-oriented routing and dependency injection.
"""

from fastapi import APIRouter
from app.models.vin import VinRequest, VinResponse
from app.services.genai_interpreter import GenAIInterpreterService

class VinRouter:
    """
    VIN Router

    Handles all VIN-related API endpoints and integrates with GenAI interpreter services.
    """
    def __init__(self):
        """
        Initialize the router and attach routes.
        """
        self.router = APIRouter()
        self.interpreter = GenAIInterpreterService()
        self.router.add_api_route(
            "/", 
            self.interpret_vin, 
            methods=["POST"], 
            response_model=VinResponse,
            summary="Interpret predictive signals for a VIN and return narrative and action pack."
        )

    def interpret_vin(self, request: VinRequest) -> VinResponse:
        """
        API endpoint: Interpret predictive signals for a given VIN.

        Args:
            request (VinRequest): The request payload containing VIN.

        Returns:
            VinResponse: The interpreted summary and recommended actions for the VIN.
        """
        return self.interpreter.interpret_vin(request.vin)
