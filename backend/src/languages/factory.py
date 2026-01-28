from backend.src.languages.base import LanguageStrategy
from backend.src.languages.python import PythonStrategy
from backend.src.languages.javascript import JavaScriptStrategy
from backend.src.languages.java import JavaStrategy

class LanguageFactory:
    """
    언어별 전략(Strategy) 객체를 생성하는 팩토리 클래스.
    """
    
    _strategies = {
        "Python": PythonStrategy(),
        "JavaScript": JavaScriptStrategy(),
        "Java": JavaStrategy(),
    }

    @classmethod
    def get_strategy(cls, language: str) -> LanguageStrategy:
        """
        선택된 언어에 맞는 전략 객체를 반환합니다.
        지원하지 않는 언어일 경우 기본값(Python)을 반환하거나 예외를 발생시킬 수 있습니다.
        """
        # 대소문자 무시 처리를 위해
        formatted_lang = next((k for k in cls._strategies.keys() if k.lower() == language.lower()), "Python")
        return cls._strategies.get(formatted_lang, cls._strategies["Python"])
    
    @classmethod
    def get_supported_languages(cls) -> list[str]:
        return list(cls._strategies.keys())
