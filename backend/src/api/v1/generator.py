import asyncio
import json
import logging

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from src.api.v1.deps import (
    get_generation_repository,
    get_test_generator_service,
    limiter,
)
from src.api.v1.generator_helper import background_save_generation
from src.auth import get_current_user, verify_turnstile
from src.exceptions import TurnstileError, ValidationError
from src.repositories.generation_repository import GenerationRepository
from src.services.test_generator_service import TestGeneratorService

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
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    service: TestGeneratorService = Depends(get_test_generator_service),
    repository: GenerationRepository = Depends(get_generation_repository),
):
    """Streams generated code using Server-Sent Events with structured error handling."""

    # 1. Turnstile Verify
    if not await verify_turnstile(data.turnstile_token):
        raise TurnstileError()

    async def generate_stream():
        generated_content = []
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
                    # Collect chunk
                    generated_content.append(chunk)
                    # Send as message event
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
                    chunk_count += 1
                    # Yield control to event loop every 100 chunks to prevent blocking
                    if chunk_count % 100 == 0:
                        await asyncio.sleep(0)

            # [System] Background Save Logic (Reliability Upgrade)
            try:
                full_code = "".join(generated_content)
                if full_code:
                    logger.info("Scheduling background save task...")
                    background_tasks.add_task(
                        background_save_generation,
                        repository=repository,
                        user_id=current_user["id"],
                        input_code=data.input_code,
                        generated_code=full_code,
                        language=data.language,
                        model=data.model,
                    )
            except Exception as e:
                logger.error(f"Failed to schedule background task: {e}", exc_info=True)

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
            logger.error(f"Streaming error: {e}", exc_info=True)
            # Send as error event
            error_data = {
                "type": "error",
                "code": "GENERATION_ERROR",
                "message": "An error occurred during generation. Please try again.",
            }
            yield format_sse_event("error", error_data)

    return StreamingResponse(generate_stream(), media_type="text/event-stream")
