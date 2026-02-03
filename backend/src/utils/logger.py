import logging
import sys
from typing import Any

from backend.src.config.settings import settings


def setup_logging() -> None:
    """애플리케이션 로깅 설정"""
    log_level = logging.DEBUG if not settings.is_production else logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # 불필요한 로그 필터링
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    구조화된 컨텍스트를 지원하는 로거 반환

    Args:
        name: 로거 이름 (일반적으로 __name__)

    Returns:
        설정된 Logger 인스턴스
    """
    logger = logging.getLogger(name)

    # 커스텀 메서드 추가 (향후 structlog 전환 준비)
    def log_with_context(level: int, msg: str, **context: Any) -> None:
        """컨텍스트 정보와 함께 로그 기록"""
        context_str = " | ".join(f"{k}={v}" for k, v in context.items())
        full_msg = f"{msg} | {context_str}" if context else msg
        logger.log(level, full_msg)

    logger.info_ctx = lambda msg, **ctx: log_with_context(logging.INFO, msg, **ctx)  # type: ignore
    logger.error_ctx = lambda msg, **ctx: log_with_context(logging.ERROR, msg, **ctx)  # type: ignore
    logger.warning_ctx = lambda msg, **ctx: log_with_context(logging.WARNING, msg, **ctx)  # type: ignore

    return logger
