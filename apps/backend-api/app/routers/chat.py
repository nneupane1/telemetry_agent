"""
Chat Router.

Provides:
- REST chat endpoint for explainability and interactive interpretation
- WebSocket chat endpoint for low-latency fallback transport
"""

from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field, ValidationError
from starlette.concurrency import run_in_threadpool

from app.services.genai_interpreter import GenAIInterpreterService
from app.utils.logger import get_logger, log_event

router = APIRouter(prefix="/chat", tags=["chat"])
logger = get_logger(__name__)

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


class ChatWebSocketRequest(ChatRequest):
    """
    Incoming WebSocket chat message.
    """

    request_id: str | None = Field(
        default=None,
        description="Optional client correlation id.",
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


@router.websocket("/ws")
async def chat_ws(websocket: WebSocket) -> None:
    """
    WebSocket chat endpoint.

    Request payload:
    {
      "message": "...",
      "context": {...},
      "request_id": "optional-id"
    }

    Success payload:
    {
      "type": "chat_response",
      "request_id": "...",
      "reply": "...",
      "transport": "websocket"
    }
    """

    await websocket.accept()
    log_event(logger, "Chat WebSocket client connected")

    try:
        while True:
            try:
                payload = await websocket.receive_json()
            except WebSocketDisconnect:
                break
            except Exception:
                await websocket.send_json(
                    {
                        "type": "error",
                        "detail": "Invalid JSON payload",
                    }
                )
                continue

            try:
                request = ChatWebSocketRequest(**payload)
            except ValidationError as exc:
                await websocket.send_json(
                    {
                        "type": "error",
                        "detail": "Invalid chat request payload",
                        "errors": exc.errors(),
                    }
                )
                continue

            try:
                reply = await run_in_threadpool(
                    genai_service.generate_chat_reply,
                    user_message=request.message,
                    context=request.context,
                    request_id=request.request_id,
                )
            except Exception:
                await websocket.send_json(
                    {
                        "type": "error",
                        "request_id": request.request_id,
                        "detail": "Failed to generate GenAI response.",
                    }
                )
                continue

            await websocket.send_json(
                {
                    "type": "chat_response",
                    "request_id": request.request_id,
                    "reply": reply,
                    "transport": "websocket",
                }
            )
    finally:
        log_event(logger, "Chat WebSocket client disconnected")
