from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from src.api.v1.deps import get_execution_service, limiter
from src.auth import get_current_user
from src.services.execution_service import ExecutionService
from src.types import AuthenticatedUser
from src.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)
# execution_service will be injected via dependency


class ExecutionRequest(BaseModel):
    """코드 실행 요청 모델.

    Attributes:
        code: 실행할 소스 코드.
        test_code: 검증용 테스트 코드.
        language: 프로그래밍 언어 (python, java, javascript).
    """

    code: str
    test_code: str
    language: str


@router.post("/execute")
@limiter.limit("10/minute")
async def execute_code(
    request: Request,
    payload: ExecutionRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service),
):
    """코드를 실행하고 테스트 결과를 반환합니다.

    제출된 소스 코드와 테스트 코드를 격리된 환경(Worker)에서 실행합니다.

    Args:
        request: HTTP 요청 객체 (Rate Limiting용).
        payload: 실행 요청 데이터 (소스 코드, 테스트 코드, 언어).
        current_user: 인증된 사용자 정보.
        service: 코드 실행 서비스 의존성.

    Returns:
        실행 결과 객체 (성공 여부, 로그, 실행 시간 등).

    Raises:
        HTTPException: 실행 요청 실패 시 (500 등).
    """
    try:
        logger.info_ctx(
            "코드 실행 요청",
            user_id=current_user["id"],
            language=payload.language,
        )

        result = await service.execute_code(
            code=payload.code,
            test_code=payload.test_code,
            language=payload.language,
        )

        logger.info_ctx(
            "코드 실행 완료",
            user_id=current_user["id"],
            success=result.get("success", False),
        )
        return result
    except Exception as e:
        logger.error(f"코드 실행 요청 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e
