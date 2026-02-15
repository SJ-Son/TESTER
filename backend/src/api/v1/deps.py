import logging
import secrets

from fastapi import Depends, HTTPException, Request
from fastapi.security import APIKeyHeader
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.config.settings import settings
from src.repositories.generation_repository import GenerationRepository
from src.services.execution_service import ExecutionService
from src.services.gemini_service import GeminiService
from src.services.supabase_service import SupabaseService
from src.services.test_generator_service import TestGeneratorService

logger = logging.getLogger(__name__)


# Rate Limiting 설정
def get_user_identifier(request: Request):
    """
    Rate Limiting을 위한 사용자 식별.
    인증된 사용자는 ID, 비로그인 사용자는 IP 사용.
    """
    user = getattr(request.state, "user", None)
    if user:
        return f"user_{user['id']}"
    return get_remote_address(request)


limiter = Limiter(key_func=get_user_identifier, storage_uri=settings.REDIS_URL)

# 보안 - 내부 API 키
API_KEY_NAME = "X-TESTER-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def verify_api_key(api_key: str = Depends(api_key_header)):
    """제공된 API 키의 유효성을 검증합니다.

    Timing Attack을 방지하기 위해 secrets.compare_digest를 사용합니다.

    Args:
        api_key (str): 헤더에서 추출한 API 키.

    Returns:
        str: 검증된 API 키.

    Raises:
        HTTPException: API 키가 유효하지 않거나 누락된 경우 (401 Unauthorized).
    """
    if not api_key or not secrets.compare_digest(
        api_key, settings.TESTER_INTERNAL_SECRET.get_secret_value()
    ):
        logger.warning(f"Unauthorized access attempt with key: {api_key}")
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Internal API Key")
    return api_key


def get_gemini_service() -> GeminiService:
    return GeminiService()


def get_execution_service() -> ExecutionService:
    return ExecutionService()


def get_supabase_service() -> SupabaseService:
    return SupabaseService()


def get_test_generator_service(
    gemini_service: GeminiService = Depends(get_gemini_service),
) -> TestGeneratorService:
    return TestGeneratorService(gemini_service=gemini_service)


def get_generation_repository(
    supabase_service: SupabaseService = Depends(get_supabase_service),
) -> GenerationRepository:
    return GenerationRepository(supabase_service=supabase_service)
