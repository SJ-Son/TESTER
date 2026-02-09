"""Java 언어 전략 구현.

Java 코드를 검증하고 JUnit 5 테스트 코드 생성을 위한 프롬프트를 제공합니다.
"""

import re
from typing import Final

from src.config.constants import ValidationConstants
from src.languages.base import LanguageStrategy
from src.types import ValidationResult


class JavaStrategy(LanguageStrategy):
    """Java 프로그래밍 언어를 위한 전략 클래스.

    키워드 패턴 매칭을 통한 검증과 JUnit 5 기반 테스트 코드 생성을 지원합니다.
    """

    _JAVA_KEYWORDS: Final[tuple[str, ...]] = (
        r"\bclass\b",
        r"\binterface\b",
        r"\bpublic\b",
        r"\bprivate\b",
        r"\bprotected\b",
        r"@Override",
    )
    """Java 코드 식별을 위한 키워드 패턴 (불변)"""

    def validate_code(self, code: str) -> ValidationResult:
        """Java 코드의 유효성을 검증합니다.

        Args:
            code: 검증할 Java 소스 코드.

        Returns:
            ValidationResult: 검증 결과.
                - 빈 코드: 에러
                - 다른 언어 패턴 감지: 에러
                - Java 키워드 없음: 에러
                - 정상: 성공
        """
        if not code.strip():
            return ValidationResult(
                is_valid=False,
                error_message=ValidationConstants.EMPTY_CODE_ERROR,
            )

        negative_check = self.check_negative_patterns(code, "java")
        if negative_check.failed:
            return negative_check

        has_java_keyword = any(re.search(keyword, code) for keyword in self._JAVA_KEYWORDS)
        if not has_java_keyword:
            return ValidationResult(
                is_valid=False,
                error_message=ValidationConstants.JAVA_SYNTAX_ERROR,
            )

        return ValidationResult(is_valid=True)

    def get_system_instruction(self) -> str:
        """Java 테스트 코드 생성을 위한 시스템 프롬프트를 반환합니다.

        Returns:
            JUnit 5 기반 테스트 코드 생성 규칙을 명시한 프롬프트.
        """
        return """
당신은 Google의 전문 Java QA 엔지니어입니다.
사용자가 입력한 Java 코드를 분석하여 `JUnit 5` 테스트 클래스를 작성합니다.

[핵심 가이드라인]
1. **[Raw Code]**: 마크다운 코드 블록(백틱)을 절대 사용하지 마십시오. 오직 순수 텍스트만 출력합니다.
2. 필요한 import 구문은 포함하되, 원본 클래스에 대한 가이드 주석은 제거하십시오.
3. **[Balanced Comments]**: 각 테스트 메서드 내부에는 무엇을 검증하는지 설명하는 간단한 한 줄 주석을 포함하십시오. (예: `// 엣지 케이스 검증`)
4. `package` 선언은 생략합니다.
5. 오직 `JUnit 5` 및 `Mockito` 기반의 순수 테스트 클래스 코드만 출력합니다.

[출력 형식]
- **[CRITICAL]**: 마크다운 코드 블록(```java ... ```)을 절대 사용하지 마십시오.
- 어떠한 마크다운 형식도 없이 오직 순수한 원본 코드(Raw Text)만 출력합니다.
- 예: import org.junit.jupiter.api.Test; ... (백틱 없이 바로 시작)
"""

    def get_placeholder(self) -> str:
        """Java 코드 입력창의 플레이스홀더를 반환합니다.

        Returns:
            간단한 Java 클래스 예시.
        """
        return "public class Calculator {\n    public int add(int a, int b) {\n        return a + b;\n    }\n}"

    def get_syntax_name(self) -> str:
        """Syntax Highlighting을 위한 언어 식별자를 반환합니다.

        Returns:
            'java'
        """
        return "java"
