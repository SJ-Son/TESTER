"""JavaScript 언어 전략 구현.

JavaScript/TypeScript 코드를 검증하고 Jest 테스트 코드 생성을 위한 프롬프트를 제공합니다.
"""

import re
from typing import Final

from src.config.constants import ValidationConstants
from src.languages.base import LanguageStrategy
from src.types import ValidationResult


class JavaScriptStrategy(LanguageStrategy):
    """JavaScript 프로그래밍 언어를 위한 전략 클래스.

    키워드 패턴 매칭을 통한 검증과 Jest 기반 테스트 코드 생성을 지원합니다.
    """

    _JS_KEYWORDS: Final[tuple[str, ...]] = (
        r"\bfunction\b",
        r"\bconst\b",
        r"\blet\b",
        r"=>",
        r"\bconsole\.log\b",
        r"\bwindow\.",
        r"\bdocument\.",
    )
    """JavaScript 코드 식별을 위한 키워드 패턴 (불변)"""

    def validate_code(self, code: str) -> ValidationResult:
        """JavaScript 코드의 유효성을 검증합니다.

        Args:
            code: 검증할 JavaScript 소스 코드.

        Returns:
            ValidationResult: 검증 결과.
                - 빈 코드: 에러
                - 다른 언어 패턴 감지: 에러
                - JS 키워드 없음: 에러
                - 정상: 성공
        """
        if not code.strip():
            return ValidationResult(
                is_valid=False,
                error_message=ValidationConstants.EMPTY_CODE_ERROR,
            )

        negative_check = self.check_negative_patterns(code, "javascript")
        if negative_check.failed:
            return negative_check

        has_js_keyword = any(re.search(keyword, code) for keyword in self._JS_KEYWORDS)
        if not has_js_keyword:
            return ValidationResult(
                is_valid=False,
                error_message=ValidationConstants.JAVASCRIPT_SYNTAX_ERROR,
            )

        return ValidationResult(is_valid=True)

    def get_system_instruction(self) -> str:
        """JavaScript 테스트 코드 생성을 위한 시스템 프롬프트를 반환합니다.

        Returns:
            Jest 기반 테스트 코드 생성 규칙을 명시한 프롬프트.
        """
        return """
당신은 Google의 전문 JavaScript QA 엔지니어입니다.
사용자가 입력한 자바스크립트 코드를 분석하여 `Jest` 테스트 코드를 작성합니다.

[핵심 가이드라인]
1. **[Raw Code]**: 마크다운 코드 블록(백틱)을 절대 사용하지 마십시오. 오직 순수 텍스트만 출력합니다.
2. 원본 함수의 재정의나 외부 Import 가이드 주석은 출력하지 마십시오.
3. **[Balanced Comments]**: 각 테스트 케이스(`it` 또는 `test`) 내부에는 무엇을 검증하는지 설명하는 간단한 한 줄 주석을 포함하십시오. (예: `// 정상 동작 검증`)
4. 모듈 시스템(CommonJS/ESM)은 입력 코드와 일치시킵니다.
5. 오직 `Jest` 기반의 순수 테스트 로직만 출력합니다.

[출력 형식]
- **[CRITICAL]**: 마크다운 코드 블록(```javascript ... ```)을 절대 사용하지 마십시오.
- 어떠한 마크다운 형식도 없이 오직 순수한 원본 코드(Raw Text)만 출력합니다.
- 예: import { ... } from ... (백틱 없이 바로 시작)
"""

    def get_placeholder(self) -> str:
        """JavaScript 코드 입력창의 플레이스홀더를 반환합니다.

        Returns:
            간단한 JavaScript 함수 예시.
        """
        return "const add = (a, b) => {\n  return a + b;\n};"

    def get_syntax_name(self) -> str:
        """Syntax Highlighting을 위한 언어 식별자를 반환합니다.

        Returns:
            'javascript'
        """
        return "javascript"
