import re

from backend.src.languages.base import LanguageStrategy


class JavaStrategy(LanguageStrategy):
    def validate_code(self, code: str) -> tuple[bool, str]:
        if not code.strip():
            return False, "코드를 입력해주세요."

        # 1. Negative Check: 다른 언어(Python, JS 등)의 패턴 감지
        valid, msg = self.check_negative_patterns(code, "java")
        if not valid:
            return False, msg

        # 2. Positive Check: Java 키워드
        java_keywords = [
            r"\bclass\b",
            r"\binterface\b",
            r"\bpublic\b",
            r"\bprivate\b",
            r"\bprotected\b",
            r"@Override",
        ]
        if not any(re.search(k, code) for k in java_keywords):
            return (
                False,
                "유효한 Java 코드가 아닌 것 같습니다. (class 정의 또는 접근 제어자가 필요합니다)",
            )

        return True, ""

    def get_system_instruction(self) -> str:
        return """
당신은 Google의 전문 Java QA 엔지니어입니다.
사용자가 입력한 Java 코드를 분석하여 `JUnit 5` 테스트 클래스를 작성합니다.

[핵심 가이드라인]
1. **[Raw Code]**: 마크다운 코드 블록(백틱)을 절대 사용하지 마십시오. 오직 순수 텍스트만 출력합니다.
2. 필여한 import 구문은 포함하되, 원본 클래스에 대한 가이드 주석은 제거하십시오.
3. **[Balanced Comments]**: 각 테스트 메서드 내부에는 무엇을 검증하는지 설명하는 간단한 한 줄 주석을 포함하십시오. (예: `// 엣지 케이스 검증`)
4. `package` 선언은 생략합니다.
5. 오직 `JUnit 5` 및 `Mockito` 기반의 순수 테스트 클래스 코드만 출력합니다.

[출력 형식]
- **[CRITICAL]**: 마크다운 코드 블록(```java ... ```)을 절대 사용하지 마십시오.
- 어떠한 마크다운 형식도 없이 오직 순수한 원본 코드(Raw Text)만 출력합니다.
- 예: import org.junit.jupiter.api.Test; ... (백틱 없이 바로 시작)
"""

    def get_placeholder(self) -> str:
        return "public class Calculator {\n    public int add(int a, int b) {\n        return a + b;\n    }\n}"

    def get_syntax_name(self) -> str:
        return "java"
