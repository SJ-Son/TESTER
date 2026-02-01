import asyncio
import logging
import os

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.src.api.v1.deps import limiter
from backend.src.auth import get_current_user, verify_recaptcha
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
    recaptcha_token: str = Field(..., description="reCAPTCHA v3 token")


@router.post("/generate")
@limiter.limit("5/minute")
async def generate_test(
    request: Request, data: GenerateRequest, current_user: dict = Depends(get_current_user)
):
    # 1. reCAPTCHA Verify
    if not await verify_recaptcha(data.recaptcha_token):
        raise HTTPException(status_code=403, detail="reCAPTCHA verification failed (Bot detected)")

    if not gemini_service:
        raise HTTPException(status_code=503, detail="Service Unavailable: AI Model not initialized")

    # 2. Logic starts...
    """Streams generated code as raw text (SSE)."""
    # 1. Validation
    try:
        strategy = LanguageFactory.get_strategy(data.language)
        valid, msg = strategy.validate_code(data.input_code)

        if not valid:
            return StreamingResponse(iter([f"ERROR: {msg}"]), media_type="text/plain")

        # 2. Setup System Instruction
        system_instruction = strategy.get_system_instruction()
        gemini_service.model_name = data.model

        async def generate_stream():
            try:
                # gemini_service.generate_test_code is now an async generator
                async for chunk in gemini_service.generate_test_code(
                    data.input_code, system_instruction=system_instruction, stream=True
                ):
                    if chunk:
                        yield chunk
                        await asyncio.sleep(0.01)

            except Exception as e:
                logger.error(f"Streaming error: {e}")
                yield f"\nERROR: {str(e)}"

        return StreamingResponse(generate_stream(), media_type="text/event-stream")
    except Exception as e:
        logger.error(f"Generate endpoint error: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e
