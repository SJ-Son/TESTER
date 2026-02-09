"""Python 언어 전략 구현.

Python 코드를 검증하고 테스트 코드 생성을 위한 프롬프트를 제공합니다.
"""

import ast

from src.config.constants import ValidationConstants
from src.languages.base import LanguageStrategy
from src.types import ValidationResult


class PythonStrategy(LanguageStrategy):
    """Python 프로그래밍 언어를 위한 전략 클래스.

    AST 파싱을 통한 문법 검증과 pytest 기반 테스트 코드 생성을 지원합니다.
    """

    def validate_code(self, code: str) -> ValidationResult:
        """Python 코드의 유효성을 검증합니다.

        Args:
            code: 검증할 Python 소스 코드.

        Returns:
            ValidationResult: 검증 결과.
                - 빈 코드: 에러
                - 다른 언어 패턴 감지: 에러
                - 문법 오류: 에러
                - 정상: 성공
        """
        if not code.strip():
            return ValidationResult(
                is_valid=False,
                error_message=ValidationConstants.EMPTY_CODE_ERROR,
            )

        negative_check = self.check_negative_patterns(code, "python")
        if negative_check.failed:
            return negative_check

        try:
            ast.parse(code)
            return ValidationResult(is_valid=True)
        except SyntaxError:
            return ValidationResult(
                is_valid=False,
                error_message=ValidationConstants.PYTHON_SYNTAX_ERROR,
            )

    def get_system_instruction(self) -> str:
        """Python 테스트 코드 생성을 위한 시스템 프롬프트를 반환합니다.

        Returns:
            pytest 기반 테스트 코드 생성 규칙을 명시한 프롬프트.
        """
        return """
당신은 Google의 전문 QA 엔지니어입니다.
사용자가 입력한 파이썬 코드를 분석하여 테스트 코드를 작성합니다.

[핵심 가이드라인]
1. **[Raw Code]**: 마크다운 코드 블록(백틱)을 절대 사용하지 마십시오. 오직 순수 텍스트만 출력합니다.
2. **[No Imports]**: 테스트 대상 함수는 **이미 같은 파일에 정의되어 있다고 가정**하십시오. `from src import ...` 등의 임포트 구문을 절대 작성하지 마십시오. 필요한 표준 라이브러리(unittest, pytest 등)만 임포트합니다.
3. 원본 함수의 재정의나 외부 Import 가이드 주석은 출력하지 마십시오.
4. **[Balanced Comments]**: 각 테스트 함수 내부에는 무엇을 검증하는지 설명하는 간단한 한 줄 주석을 포함하십시오. (예: `# 정상 범위 입력 테스트`)
5. 전체적인 설명이나 부연 설명은 여전히 금지하며, 오직 코드와 내부의 최소한의 주석만 출력합니다.
6. 오직 `pytest` 기반의 순수 테스트 로직만 출력합니다.

[출력 형식]
- **[CRITICAL]**: 마크다운 코드 블록(```python ... ```)을 절대 사용하지 마십시오.
- 어떠한 마크다운 형식도 없이 오직 순수한 원본 코드(Raw Text)만 출력합니다.
- 예: import pytest ... (백틱 없이 바로 시작)
"""

    def get_placeholder(self) -> str:
        """Python 코드 입력창의 플레이스홀더를 반환합니다.

        Returns:
            간단한 Python 함수 예시.
        """
        return "def add(a, b):\n    return a + b"

    def get_syntax_name(self) -> str:
        """Syntax Highlighting을 위한 언어 식별자를 반환합니다.

        Returns:
            'python'
        """
        return "python"
