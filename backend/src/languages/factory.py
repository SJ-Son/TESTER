from backend.src.exceptions import UnsupportedLanguageError
from backend.src.languages.base import LanguageStrategy
from backend.src.languages.java import JavaStrategy
from backend.src.languages.javascript import JavaScriptStrategy
from backend.src.languages.python import PythonStrategy


class LanguageFactory:
    """언어별 검증 및 프롬프트 전략을 관리하는 팩토리 (싱글톤)"""

    _instances: dict[str, LanguageStrategy] = {}

    @classmethod
    def get_strategy(cls, language: str) -> LanguageStrategy:
        """
        언어에 맞는 Strategy 인스턴스를 반환 (캐싱됨)

        Args:
            language: 프로그래밍 언어 (python, javascript, java)

        Returns:
            해당 언어의 LanguageStrategy 인스턴스

        Raises:
            UnsupportedLanguageError: 지원하지 않는 언어인 경우
        """
        language = language.lower()

        # 캐싱된 인스턴스 반환
        if language in cls._instances:
            return cls._instances[language]

        # 언어별 전략 매핑
        strategies = {
            "python": PythonStrategy,
            "javascript": JavaScriptStrategy,
            "java": JavaStrategy,
        }

        strategy_class = strategies.get(language)
        if not strategy_class:
            raise UnsupportedLanguageError(f"Language '{language}' is not supported")

        # 새 인스턴스 생성 및 캐싱
        cls._instances[language] = strategy_class()
        return cls._instances[language]

    @classmethod
    def get_supported_languages(cls) -> list[str]:
        """지원하는 언어 목록 반환"""
        return ["python", "javascript", "java"]

    @classmethod
    def clear_cache(cls):
        """테스트용: 캐시 초기화"""
        cls._instances.clear()
