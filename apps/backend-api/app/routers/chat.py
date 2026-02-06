"""
Chat Router.

Provides a controlled GenAI chat endpoint for
explainability and interactive interpretation.
"""

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from app.services.genai_interpreter import GenAIInterpreterService

router = APIRouter(prefix="/chat", tags=["chat"])

genai_service = GenAIInterpreterService()

# ------------------------------------------------------------
# Request / Response models
# ------------------------------------------------------------

class ChatRequest(BaseModel):
    """
    Incoming chat message from the UI.
    """
    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="User question about predictive data."
    )
    context: dict | None = Field(
        default=None,
        description="Optional VIN / cohort context."
    )


class ChatResponse(BaseModel):
    """
    GenAI-generated response.
    """
    reply: str = Field(
        ...,
        description="Bounded, natural-language explanation."
    )


# ------------------------------------------------------------
# Endpoint
# ------------------------------------------------------------

@router.post("", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    x_request_id: str | None = Header(default=None),
) -> ChatResponse:
    """
    POST /chat

    Generates a controlled GenAI explanation in response
    to a user question.

    This endpoint is scoped to:
    - predictive maintenance interpretation
    - fleet / VIN / cohort context
    """

    try:
        reply = genai_service.generate_chat_reply(
            user_message=request.message,
            context=request.context,
            request_id=x_request_id,
        )

        return ChatResponse(reply=reply)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate GenAI response.",
        ) from exc
