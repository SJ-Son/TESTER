import logging
import sys
from typing import Any


def setup_logging(log_level: int = logging.INFO) -> None:
    """
    애플리케이션 로깅 설정

    Args:
        log_level: 로그 레벨 (기본값: INFO)
    """
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
        name (str): Logger name, typically __name__ of the calling module.

    Returns:
        logging.Logger: A configured logger instance.
    """
    logger = logging.getLogger(name)

    # 컨텍스트 정보를 포함한 로깅 메서드 추가
    def log_with_context(level: int, msg: str, **context: Any) -> None:
        """컨텍스트 정보와 함께 로그 기록"""
        if context:
            context_str = " | ".join(f"{k}={v}" for k, v in context.items())
            full_msg = f"{msg} | {context_str}"
        else:
            full_msg = msg
        logger.log(level, full_msg)

    # 타입 무시 주석으로 mypy 경고 회피
    logger.info_ctx = lambda msg, **ctx: log_with_context(logging.INFO, msg, **ctx)  # type: ignore
    logger.error_ctx = lambda msg, **ctx: log_with_context(logging.ERROR, msg, **ctx)  # type: ignore
    logger.warning_ctx = lambda msg, **ctx: log_with_context(logging.WARNING, msg, **ctx)  # type: ignore

    return logger
