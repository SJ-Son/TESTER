from backend.src.languages.base import LanguageStrategy
from backend.src.languages.java import JavaStrategy
from backend.src.languages.javascript import JavaScriptStrategy
from backend.src.languages.python import PythonStrategy


class UnsupportedLanguageError(Exception):
    """지원하지 않는 언어에 대한 예외"""

    pass


class LanguageFactory:
    """
    언어별 전략(Strategy) 객체를 생성하는 팩토리 클래스.
    싱글톤 패턴을 사용하여 인스턴스를 재사용합니다.
    """

    _strategy_classes = {
        "python": PythonStrategy,
        "javascript": JavaScriptStrategy,
        "java": JavaStrategy,
    }

    # 인스턴스 캐시
    _instances: dict[str, LanguageStrategy] = {}

    @classmethod
    def get_strategy(cls, language: str) -> LanguageStrategy:
        """
        선택된 언어에 맞는 전략 객체를 반환합니다.
        인스턴스는 처음 요청 시 생성되어 캐시됩니다.
        """
        lang_key = language.lower()

        # 캐시에서 확인
        if lang_key in cls._instances:
            return cls._instances[lang_key]

        # 지원하지 않는 언어 처리
        if lang_key not in cls._strategy_classes:
            raise UnsupportedLanguageError(
                f"Unsupported language: {language}. "
                f"Supported languages: {', '.join(cls.get_supported_languages())}"
            )

        # 인스턴스 생성 및 캐싱
        strategy_class = cls._strategy_classes[lang_key]
        cls._instances[lang_key] = strategy_class()
        return cls._instances[lang_key]

    @classmethod
    def get_supported_languages(cls) -> list[str]:
        """지원하는 언어 목록을 반환합니다."""
        return [lang.capitalize() for lang in cls._strategy_classes.keys()]
