import asyncio
import json

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from src.api.v1.deps import (
    get_generation_repository,
    get_test_generator_service,
    get_token_service,
    limiter,
)
from src.auth import get_current_user, validate_turnstile_token
from src.config.constants import TokenConstants
from src.exceptions import InsufficientTokensError, ValidationError
from src.repositories.generation_repository import GenerationRepository
from src.services.test_generator_service import TestGeneratorService
from src.services.token_service import TokenService
from src.types import AuthenticatedUser, GenerateRequest
from src.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


def format_sse_event(event_type: str, data: dict) -> str:
    """SSE 이벤트 데이터 포맷팅."""
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


@router.post("/generate")
@limiter.limit("5/minute")
async def generate_test(
    request: Request,
    data: GenerateRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: TestGeneratorService = Depends(get_test_generator_service),
    repository: GenerationRepository = Depends(get_generation_repository),
    token_service: TokenService = Depends(get_token_service),
):
    """테스트 코드 생성 및 스트리밍 반환 (SSE).

    사용자 입력 코드를 기반으로 테스트 코드를 생성하고,
    Server-Sent Events(SSE)를 통해 청크 단위로 스트리밍합니다.
    생성 전 토큰을 차감하고, 실패 시 자동으로 환불합니다.

    Args:
        request: HTTP 요청 객체 (Rate Limiting용).
        data: 생성 요청 데이터 (코드, 언어, 모델 등).
        current_user: 인증된 사용자 정보.
        service: 테스트 생성 서비스 의존성.
        repository: 생성 이력 저장소 의존성.
        token_service: 토큰 관리 서비스 의존성.

    Returns:
        SSE 스트림 응답.

    Raises:
        InsufficientTokensError: 토큰 부족 시 (402).
    """

    # 1. Turnstile 검증
    client_ip = request.client.host if request.client else None
    await validate_turnstile_token(data.turnstile_token, ip=client_ip)

    async def generate_stream():
        # 2. 토큰 차감 (Atomic — 스트리밍 전에 선차감)
        tokens_deducted = False
        try:
            deduct_result = await token_service.deduct_tokens(
                user_id=current_user["id"],
                amount=TokenConstants.COST_PER_GENERATION,
            )
            tokens_deducted = deduct_result.success

            if not deduct_result.success:
                yield f"data: {json.dumps({'type': 'error', 'code': 'INSUFFICIENT_TOKENS', 'message': '토큰이 부족합니다.', 'required': TokenConstants.COST_PER_GENERATION, 'current': deduct_result.current_balance})}\n\n"
                return

        except InsufficientTokensError as e:
            yield f"data: {json.dumps({'type': 'error', 'code': 'INSUFFICIENT_TOKENS', 'message': str(e), 'required': e.required, 'current': e.current})}\n\n"
            return
        except Exception as e:
            logger.error(f"토큰 차감 실패: {e}")
            # Fail Open: 토큰 차감 실패 시에도 생성은 허용 (로그 기록)
            pass

        logger.info_ctx(
            "테스트 코드 생성 요청",
            user_id=current_user["id"],
            language=data.language,
            model=data.model,
        )

        generated_content = []
        generation_success = False
        try:
            chunk_count = 0
            async for chunk in service.generate_test(
                code=data.input_code,
                language=data.language,
                model=data.model,
                is_regenerate=data.is_regenerate,
            ):
                if chunk:
                    generated_content.append(chunk)
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
                    chunk_count += 1
                    if chunk_count % 100 == 0:
                        await asyncio.sleep(0)

            # 생성된 코드 저장
            full_code = "".join(generated_content)
            if full_code:
                generation_success = True
                yield format_sse_event(
                    "status", {"step": "saving_history", "message": "생성 이력을 저장 중입니다..."}
                )
                try:
                    logger.info("생성 이력 저장 중...")
                    saved = await repository.create_history(
                        user_id=current_user["id"],
                        input_code=data.input_code,
                        generated_code=full_code,
                        language=data.language,
                        model=data.model,
                    )
                    if saved:
                        logger.info_ctx("이력 저장 성공", history_id=saved.id)
                except Exception as e:
                    logger.error(f"이력 저장 실패: {e}")
                    yield format_sse_event(
                        "warning",
                        {
                            "message": "코드 저장에 실패했습니다. 생성된 코드를 복사하여 별도로 저장해주세요."
                        },
                    )

            # 완료 이벤트 전송
            yield format_sse_event("message", {"type": "done"})

        except ValidationError as e:
            logger.warning(f"Validation failed: {e}")
            yield format_sse_event(
                "error",
                {"code": "VALIDATION_ERROR", "message": str(e)},
            )

        except Exception as e:
            logger.error(f"Streaming error: {e}", exc_info=True)
            error_data = {
                "type": "error",
                "code": "GENERATION_ERROR",
                "message": "An error occurred during generation. Please try again.",
            }
            yield format_sse_event("error", error_data)

        finally:
            # 생성 실패 시 토큰 환불
            if tokens_deducted and not generation_success:
                logger.info_ctx(
                    "생성 실패로 인한 토큰 환불 시도",
                    user_id=current_user["id"],
                    amount=TokenConstants.COST_PER_GENERATION,
                )
                await token_service.refund_tokens(
                    user_id=current_user["id"],
                    amount=TokenConstants.COST_PER_GENERATION,
                )

    return StreamingResponse(generate_stream(), media_type="text/event-stream")
