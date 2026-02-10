"""다국어 지원을 위한 Strategy 패턴 기반 추상 클래스.

각 프로그래밍 언어는 LanguageStrategy를 상속하여 검증 로직, 프롬프트,
UI 설정을 정의합니다. 불변성과 순수 함수를 지향합니다.
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Final

from src.types import ValidationResult


@dataclass(frozen=True)
class LanguagePattern:
    """언어 감지 패턴을 나타내는 불변 데이터 구조.

    Attributes:
        regex: 언어별 특징적인 패턴을 매칭하는 정규표현식.
        error_message: 패턴 감지 시 반환할 에러 메시지.
    """

    regex: str
    error_message: str


class LanguageStrategy(ABC):
    """다국어 지원을 위한 추상 기본 클래스.

    각 언어별 검증 로직, 프롬프트, UI 설정 등을 정의합니다.
    모든 메서드는 순수 함수로 구현되어야 하며, 상태를 변경하지 않습니다.
    """

    # 각 언어 감지용 패턴 (불변)
    _LANGUAGE_PATTERNS: Final[dict[str, LanguagePattern]] = {
        "python": LanguagePattern(
            regex=r"^\s*def\s+\w+\s*\(.*\)\s*:",
            error_message="Python 코드로 감지됩니다. 언어 설정을 'Python'으로 변경해주세요.",
        ),
        "javascript": LanguagePattern(
            regex=r"\bconsole\.log\b|\bfunction\s+\w+\s*\(|\bconst\s+\w+\s*=|=>|\blet\s+\w+\b",
            error_message="JavaScript 코드로 감지됩니다. 언어 설정을 'JavaScript'로 변경해주세요.",
        ),
        "java": LanguagePattern(
            regex=r"\bpublic\s+(?:class|interface|void|int|double|String|boolean)\b|\bprivate\s+\w+\b|\bprotected\s+\w+\b|\bSystem\.out\.println\b",
            error_message="Java 코드로 감지됩니다. 언어 설정을 'Java'로 변경해주세요.",
        ),
    }

    def check_negative_patterns(self, code: str, current_lang: str) -> ValidationResult:
        """타 언어의 특징적인 패턴이 포함되어 있는지 검증합니다.

        현재 선택된 언어가 아닌 다른 언어의 패턴이 감지될 경우
        사용자에게 올바른 언어 선택을 권장합니다.

        Args:
            code: 검증할 소스 코드.
            current_lang: 현재 선택된 언어 (소문자).

        Returns:
            ValidationResult: 검증 결과 (성공 또는 에러 메시지 포함).

        Example:
            >>> strategy = PythonStrategy()
            >>> result = strategy.check_negative_patterns("console.log('test')", "python")
            >>> result.is_valid
            False
        """
        for lang, pattern in self._LANGUAGE_PATTERNS.items():
            if lang == current_lang.lower():
                continue

            if re.search(pattern.regex, code, re.MULTILINE):
                return ValidationResult(is_valid=False, error_message=pattern.error_message)

        return ValidationResult(is_valid=True)

    @abstractmethod
    def validate_code(self, code: str) -> ValidationResult:
        """입력된 코드가 해당 언어의 문법에 맞는지 검증합니다.

        최소한의 키워드, 구문 패턴 등을 확인하여 유효성을 판단합니다.
        부작용 없는 순수 함수로 구현해야 합니다.

        Args:
            code: 검증할 소스 코드.

        Returns:
            ValidationResult: 검증 결과 (성공 또는 에러 메시지 포함).
        """
        pass

    @abstractmethod
    def get_system_instruction(self) -> str:
        """해당 언어의 QA 엔지니어 역할을 수행하기 위한 시스템 프롬프트를 반환합니다.

        AI 모델에게 전달되는 시스템 지시문으로, 언어별 테스트 코드 생성 규칙을
        명확히 정의합니다.

        Returns:
            시스템 프롬프트 문자열.
        """
        pass

    @abstractmethod
    def get_placeholder(self) -> str:
        """UI 입력창에 보여줄 예시 코드를 반환합니다.

        사용자에게 해당 언어의 전형적인 코드 형식을 보여주는 용도입니다.

        Returns:
            플레이스홀더 코드 문자열.
        """
        pass

    @abstractmethod
    def get_syntax_name(self) -> str:
        """Syntax Highlighting에 사용할 언어 식별자를 반환합니다.

        Prism.js, highlight.js 등의 라이브러리에서 사용하는 언어 이름입니다.

        Returns:
            언어 식별자 (예: 'python', 'javascript', 'java').
        """
        pass
