"""
Defines request and response models for VIN interpretation endpoints.
"""

from pydantic import BaseModel, Field


class VinRequest(BaseModel):
    """
    Represents a request payload to interpret a specific vehicle VIN.
    """
    vin: str = Field(..., description="Vehicle Identification Number for analysis.")


class ActionPack(BaseModel):
    """
    Contains the operational recommendations and confidence for a vehicle.
    """
    recommendation: str = Field(..., description="Operational recommendation for the vehicle.")
    confidence: str = Field(..., description="Confidence level in the recommendation.")


class VinResponse(BaseModel):
    """
    Full response containing the interpreted summary and recommended actions for a VIN.
    """
    vin: str = Field(..., description="Vehicle Identification Number analyzed.")
    summary: str = Field(..., description="Natural-language summary of predictive insights for this VIN.")
    action_pack: ActionPack = Field(..., description="Recommended operational actions and confidence for this VIN.")
