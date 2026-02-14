import asyncio
import json

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from src.api.v1.deps import (
    get_generation_repository,
    get_supabase_service,
    get_test_generator_service,
    limiter,
)
from src.auth import get_current_user, validate_turnstile_token
from src.exceptions import ValidationError
from src.repositories.generation_repository import GenerationRepository
from src.services.supabase_service import SupabaseService
from src.services.test_generator_service import TestGeneratorService
from src.types import AuthenticatedUser, GenerateRequest
from src.utils.logger import get_logger
from starlette.concurrency import run_in_threadpool

router = APIRouter()
logger = get_logger(__name__)


def format_sse_event(event_type: str, data: dict) -> str:
    """SSE 이벤트 데이터 포맷팅"""
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


@router.post("/generate")
@limiter.limit("5/minute")
async def generate_test(
    request: Request,
    data: GenerateRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: TestGeneratorService = Depends(get_test_generator_service),
    repository: GenerationRepository = Depends(get_generation_repository),
    supabase_service: SupabaseService = Depends(get_supabase_service),
):
    """테스트 코드 생성 및 스트리밍 반환 (SSE).

    사용자 입력 코드를 기반으로 테스트 코드를 생성하고,
    Server-Sent Events(SSE)를 통해 청크 단위로 스트리밍합니다.

    Args:
        request: HTTP 요청 객체 (Rate Limiting용).
        data: 생성 요청 데이터 (코드, 언어, 모델 등).
        current_user: 인증된 사용자 정보.
        service: 테스트 생성 서비스 의존성.
        repository: 생성 이력 저장소 의존성.
        supabase_service: Supabase 서비스 의존성 (쿼터 확인용).

    Returns:
        SSE 스트림 응답.

    Raises:
        HTTPException: 주간 쿼터 초과 시 (429).
    """

    # 1. Turnstile 검증
    # context에 IP 주소 추가를 위해 request 객체 활용 가능
    client_ip = request.client.host if request.client else None
    await validate_turnstile_token(data.turnstile_token, ip=client_ip)

    async def generate_stream():
        # 2. 주간 쿼터 확인 (30회/주) - 스트림 내부로 이동
        # Redis 캐싱을 적용하여 DB 부하 최소화
        try:
            current_usage = await supabase_service.get_weekly_quota(current_user["id"])

            WEEKLY_LIMIT = 30
            if current_usage >= WEEKLY_LIMIT:
                logger.warning_ctx(
                    "주간 쿼터 초과",
                    user_id=current_user["id"],
                    usage=current_usage,
                    limit=WEEKLY_LIMIT,
                )
                yield f"data: {json.dumps({'type': 'error', 'message': f'주간 사용량({current_usage}/{WEEKLY_LIMIT})을 초과했습니다.'})}\n\n"
                return

        except Exception as e:
            logger.error(f"쿼터 확인 실패: {e}")
            # 실패 시 Fail Open (로그만 남기고 진행)
            pass

        logger.info_ctx(
            "테스트 코드 생성 요청",
            user_id=current_user["id"],
            language=data.language,
            model=data.model,
        )

        generated_content = []
        try:
            chunk_count = 0
            # 생성 로직 위임
            async for chunk in service.generate_test(
                code=data.input_code,
                language=data.language,
                model=data.model,
                is_regenerate=data.is_regenerate,
            ):
                if chunk:
                    # 청크 수집
                    generated_content.append(chunk)
                    # 메시지 이벤트 전송
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
                    chunk_count += 1
                    # 100 청크마다 이벤트 루프 양보 (블로킹 방지)
                    if chunk_count % 100 == 0:
                        await asyncio.sleep(0)

            # 생성된 코드 저장 (동기 처리로 변경 - 데이터 손실 방지)
            full_code = "".join(generated_content)
            if full_code:
                yield format_sse_event(
                    "status", {"step": "saving_history", "message": "생성 이력을 저장 중입니다..."}
                )
                try:
                    logger.info("생성 이력 저장 중...")
                    saved = await run_in_threadpool(
                        repository.create_history,
                        user_id=current_user["id"],
                        input_code=data.input_code,
                        generated_code=full_code,
                        language=data.language,
                        model=data.model,
                    )
                    if saved:
                        logger.info_ctx("이력 저장 성공", history_id=saved.id)
                        # 이력 저장 성공 시 캐시된 쿼터 증가 (비동기)
                        await supabase_service.increment_quota_cache(current_user["id"])
                except Exception as e:
                    logger.error(f"이력 저장 실패: {e}")
                    # 사용자에게는 성공 응답을 보냈으므로 에러를 던지지 않음
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
