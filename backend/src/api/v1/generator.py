import asyncio
import json
import logging
import os

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.src.api.v1.deps import limiter
from backend.src.auth import get_current_user, verify_turnstile
from backend.src.exceptions import GenerationError, TurnstileError, ValidationError
from backend.src.languages.factory import LanguageFactory
from backend.src.services.gemini_service import GeminiService

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize Service
try:
    if not os.getenv("GEMINI_API_KEY"):
        logger.warning("GEMINI_API_KEY not found in env. Service might fail.")
    gemini_service = GeminiService(model_name="gemini-3-flash-preview")
except Exception as e:
    logger.error(f"Failed to initialize GeminiService: {e}")
    gemini_service = None


class GenerateRequest(BaseModel):
    input_code: str
    language: str
    model: str = "gemini-3-flash-preview"
    turnstile_token: str = Field(..., description="Cloudflare Turnstile token")


def format_sse_event(event_type: str, data: dict) -> str:
    """Format data as Server-Sent Event."""
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


@router.post("/generate")
@limiter.limit("5/minute")
async def generate_test(
    request: Request, data: GenerateRequest, current_user: dict = Depends(get_current_user)
):
    """Streams generated code using Server-Sent Events with structured error handling."""

    # 1. Turnstile Verify
    if not await verify_turnstile(data.turnstile_token):
        raise TurnstileError()

    if not gemini_service:
        raise HTTPException(status_code=503, detail="Service Unavailable: AI Model not initialized")

    # 2. Validation
    try:
        strategy = LanguageFactory.get_strategy(data.language)
        valid, msg = strategy.validate_code(data.input_code)

        if not valid:
            raise ValidationError(msg)

        # 3. Setup System Instruction
        system_instruction = strategy.get_system_instruction()
        gemini_service.model_name = data.model

        async def generate_stream():
            try:
                async for chunk in gemini_service.generate_test_code(
                    data.input_code, system_instruction=system_instruction, stream=True
                ):
                    if chunk:
                        # Send as message event
                        yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
                        await asyncio.sleep(0.01)

                # Send completion event
                yield format_sse_event("message", {"type": "done"})

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

    except ValidationError as e:
        logger.warning(f"Validation failed: {e.message}")
        # Return 200 OK with error payload to keep the browser console clean
        return {
            "type": "error",
            "status": "validation_error",
            "detail": {"code": e.code, "message": e.message},
        }
    except TurnstileError as e:
        logger.error(f"Turnstile failed: {e.message}")
        raise HTTPException(
            status_code=403, detail={"code": e.code, "message": e.message}
        ) from None
    except Exception as e:
        logger.error(f"Generate endpoint error: {e}")
        raise GenerationError(str(e)) from e
