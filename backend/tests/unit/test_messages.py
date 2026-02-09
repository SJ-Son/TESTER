"""Messages classes 단위 테스트 - 간단 버전."""

from src.config.messages import ErrorMessages, InfoMessages, LogMessages


def test_error_messages_attributes():
    """ErrorMessages 클래스에 메시지 속성이 있는지 테스트."""
    assert hasattr(ErrorMessages, "EMPTY_CODE")
    assert hasattr(ErrorMessages, "API_KEY_MISSING")


def test_info_messages_attributes():
    """InfoMessages 클래스에 메시지 속성이 있는지 테스트."""
    assert hasattr(InfoMessages, "CACHE_HIT")
    assert hasattr(InfoMessages, "GENERATION_STARTED")


def test_log_messages_attributes():
    """LogMessages 클래스에 메시지 속성이 있는지 테스트."""
    assert hasattr(LogMessages, "REDIS_CONNECTED")
    assert hasattr(LogMessages, "SERVER_STARTED")
