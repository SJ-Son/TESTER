from abc import ABC, abstractmethod
import re

class LanguageStrategy(ABC):
    """
    다국어 지원을 위한 추상 기본 클래스.
    각 언어별 검증 로직, 프롬프트, UI 설정 등을 정의합니다.
    """

    def check_negative_patterns(self, code: str, current_lang: str) -> tuple[bool, str]:
        """
        타 언어의 특징적인 패턴이 포함되어 있는지 검증하는 공통 헬퍼 메서드입니다.
        (DRY 개선: 기존 각 전략 파일에 파편화되어 있던 로직을 통합)
        """
        patterns = {
            "python": {
                "regex": r'^\s*def\s+\w+\s*\(.*\)\s*:',
                "msg": "Python 코드로 감지됩니다. 언어 설정을 'Python'으로 변경해주세요."
            },
            "javascript": {
                "regex": r'\bconsole\.log\b|\bfunction\s+\w+\s*\(',
                "msg": "JavaScript 코드로 감지됩니다. 언어 설정을 'JavaScript'로 변경해주세요."
            },
            "java": {
                "regex": r'\bpublic\s+static\s+void\b|\bSystem\.out\.println\b',
                "msg": "Java 코드로 감지됩니다. 언어 설정을 'Java'로 변경해주세요."
            }
        }
        
        for lang, data in patterns.items():
            if lang == current_lang.lower():
                continue
            if re.search(data["regex"], code, re.MULTILINE):
                return False, data["msg"]
        
        return True, ""

    @abstractmethod
    def validate_code(self, code: str) -> tuple[bool, str]:
        """
        입력된 코드가 해당 언어의 문법에 맞는지(또는 최소한의 키워드가 있는지) 검증합니다.
        
        Returns:
            (is_valid, error_message)
        """
        pass

    @abstractmethod
    def get_system_instruction(self) -> str:
        """
        해당 언어의 QA 엔지니어 역할을 수행하기 위한 시스템 프롬프트를 반환합니다.
        """
        pass

    @abstractmethod
    def get_placeholder(self) -> str:
        """
        UI 입력창에 보여줄 예시 코드를 반환합니다.
        """
        pass
    
    @abstractmethod
    def get_syntax_name(self) -> str:
        """
        Syntax Highlighting에 사용할 언어 식별자를 반환합니다.
        예: 'python', 'javascript', 'java'
        """
        pass
