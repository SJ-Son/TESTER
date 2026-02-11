import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any

# Trace ID를 저장할 ContextVar
trace_id_ctx: ContextVar[str | None] = ContextVar("trace_id", default=None)


class JSONFormatter(logging.Formatter):
    """로그를 JSON 형식으로 포맷팅하는 클래스."""

    def format(self, record: logging.LogRecord) -> str:
        """LogRecord를 JSON 문자열로 변환합니다.

        Args:
            record: 로깅 레코드 객체.

        Returns:
            JSON 형식의 로그 문자열.
        """
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "trace_id": trace_id_ctx.get(),
        }

        if hasattr(record, "context"):
            log_data.update(record.context)

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(log_level: int = logging.INFO) -> None:
    """애플리케이션 로깅 설정을 초기화합니다.

    JSON 포맷터를 사용하여 표준 출력으로 로그를 전송하도록 설정합니다.

    Args:
        log_level: 로그 레벨 (기본값: INFO).
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = [handler]

    # 불필요한 로그 필터링
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """구조화된 컨텍스트를 지원하는 로거를 반환합니다.

    Args:
        name: 로거 이름 (보통 __name__ 사용).

    Returns:
        설정된 로거 인스턴스.
    """
    logger = logging.getLogger(name)

    # 컨텍스트 정보를 포함한 로깅 메서드 추가
    def log_with_context(level: int, msg: str, **context: Any) -> None:
        """컨텍스트 정보와 함께 로그를 기록합니다."""
        extra = {"context": context}
        logger.log(level, msg, extra=extra)

    # 타입 무시 주석으로 mypy 경고 회피
    logger.info_ctx = lambda msg, **ctx: log_with_context(logging.INFO, msg, **ctx)  # type: ignore
    logger.error_ctx = lambda msg, **ctx: log_with_context(logging.ERROR, msg, **ctx)  # type: ignore
    logger.warning_ctx = lambda msg, **ctx: log_with_context(logging.WARNING, msg, **ctx)  # type: ignore

    return logger
