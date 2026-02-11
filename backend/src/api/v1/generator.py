import asyncio
import json
import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from src.api.v1.deps import (
    get_generation_repository,
    get_test_generator_service,
    limiter,
    validate_turnstile_token_dep,
)
from src.auth import get_current_user
from src.exceptions import ValidationError
from src.repositories.generation_repository import GenerationRepository
from src.services.test_generator_service import TestGeneratorService
from src.types import AuthenticatedUser, GenerateRequest
from starlette.concurrency import run_in_threadpool

router = APIRouter()
logger = logging.getLogger(__name__)


def format_sse_event(event_type: str, data: dict) -> str:
    """Format data as Server-Sent Event."""
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


@router.post("/generate")
@limiter.limit("5/minute")
async def generate_test(
    request: Request,
    data: GenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: TestGeneratorService = Depends(get_test_generator_service),
    repository: GenerationRepository = Depends(get_generation_repository),
    _: None = Depends(validate_turnstile_token_dep),
):
    """Streams generated code using Server-Sent Events with structured error handling."""

    # 1. Turnstile Verify - Handled by dependency
    # validate_turnstile_token(data.turnstile_token) is called by Depends

    # 2. Weekly Quota Check (30/week)
    try:
        from src.services.supabase_service import SupabaseService

        supabase = SupabaseService()
        current_usage = await run_in_threadpool(supabase.check_weekly_quota, current_user["id"])

        WEEKLY_LIMIT = 30
        if current_usage >= WEEKLY_LIMIT:
            raise HTTPException(
                status_code=429,
                detail=f"Weekly quota exceeded. You used {current_usage}/{WEEKLY_LIMIT} requests in the last 7 days.",
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Quota check failed: {e}")
        # Fail open if check fails, but log error
        pass

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

            # 생성된 코드 저장 (동기 처리로 변경 - 데이터 손실 방지)
            full_code = "".join(generated_content)
            if full_code:
                try:
                    logger.info("Saving generation history...")
                    saved = await run_in_threadpool(
                        repository.create_history,
                        user_id=current_user["id"],
                        input_code=data.input_code,
                        generated_code=full_code,
                        language=data.language,
                        model=data.model,
                    )
                    if saved:
                        logger.info(f"History saved successfully: {saved.id}")
                except Exception as e:
                    logger.error(f"Failed to save history: {e}", exc_info=True)
                    # 사용자에게 경고 전송
                    yield format_sse_event(
                        "warning",
                        {
                            "message": "코드 저장에 실패했습니다. 생성된 코드를 복사하여 별도로 저장해주세요."
                        },
                    )

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
