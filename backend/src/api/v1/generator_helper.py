import logging

from src.repositories.generation_repository import GenerationRepository
from starlette.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)


async def background_save_generation(
    repository: GenerationRepository,
    user_id: str,
    input_code: str,
    generated_code: str,
    language: str,
    model: str,
) -> None:
    """생성된 코드 이력을 백그라운드에서 저장합니다.

    응답 지연을 최소화하기 위해 비동기 백그라운드 작업으로 실행됩니다.
    실패 시 로그를 남기고 무시합니다 (Fire-and-forget).

    Args:
        repository: 생성 이력 저장소 인스턴스.
        user_id: 사용자 ID.
        input_code: 사용자 입력 코드.
        generated_code: 생성된 테스트 코드.
        language: 프로그래밍 언어.
        model: 사용된 AI 모델명.
    """
    try:
        logger.info_ctx(
            "백그라운드 이력 저장 시작",
            user_id=user_id,
        )
        saved = await run_in_threadpool(
            repository.create_history,
            user_id=user_id,
            input_code=input_code,
            generated_code=generated_code,
            language=language,
            model=model,
        )
        if saved:
            logger.info_ctx("백그라운드 이력 저장 완료", history_id=saved.id)
    except Exception as e:
        logger.error(f"백그라운드 이력 저장 실패: {e}", exc_info=True)
