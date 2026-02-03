import asyncio
import json
import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.src.api.v1.deps import get_test_generator_service, limiter
from backend.src.auth import get_current_user, verify_turnstile
from backend.src.exceptions import TurnstileError, ValidationError
from backend.src.services.test_generator_service import TestGeneratorService

router = APIRouter()
logger = logging.getLogger(__name__)


class GenerateRequest(BaseModel):
    input_code: str
    language: str
    model: str = "gemini-3-flash-preview"
    turnstile_token: str = Field(..., description="Cloudflare Turnstile token")
    is_regenerate: bool = False


def format_sse_event(event_type: str, data: dict) -> str:
    """Format data as Server-Sent Event."""
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


@router.post("/generate")
@limiter.limit("5/minute")
async def generate_test(
    request: Request,
    data: GenerateRequest,
    current_user: dict = Depends(get_current_user),
    service: TestGeneratorService = Depends(get_test_generator_service),
):
    """Streams generated code using Server-Sent Events with structured error handling."""

    # 1. Turnstile Verify
    if not await verify_turnstile(data.turnstile_token):
        raise TurnstileError()

    async def generate_stream():
        try:
            chunk_count = 0
            # Delegate logic to Service
            async for chunk in service.generate_test(
                code=data.input_code,
                language=data.language,
                model=data.model,
                is_regenerate=data.is_regenerate,
            ):
                if chunk:
                    # Send as message event
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
                    chunk_count += 1
                    # Yield control to event loop every 100 chunks to prevent blocking
                    if chunk_count % 100 == 0:
                        await asyncio.sleep(0)

            # Send completion event
            yield format_sse_event("message", {"type": "done"})

        except ValidationError as e:
            logger.warning(f"Validation failed: {e}")
            # Send as error event via SSE
            yield format_sse_event(
                "error",
                {"code": "VALIDATION_ERROR", "message": str(e)},
            )

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            # Send as error event
            error_data = {
                "type": "error",
                "code": "GENERATION_ERROR",
                "message": str(e),
            }
            yield format_sse_event("error", error_data)

    return StreamingResponse(generate_stream(), media_type="text/event-stream")
