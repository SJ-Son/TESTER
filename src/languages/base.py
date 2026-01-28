from abc import ABC, abstractmethod

class LanguageStrategy(ABC):
    """
    다국어 지원을 위한 추상 기본 클래스.
    각 언어별 검증 로직, 프롬프트, UI 설정 등을 정의합니다.
    """

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
