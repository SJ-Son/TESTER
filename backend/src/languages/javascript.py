import re

from backend.src.languages.base import LanguageStrategy


class JavaScriptStrategy(LanguageStrategy):
    def validate_code(self, code: str) -> tuple[bool, str]:
        if not code.strip():
            return False, "코드를 입력해주세요."

        # 1. Negative Check: 다른 언어(Python, Java 등)의 강력한 특징이 있는가?
        valid, msg = self.check_negative_patterns(code, "javascript")
        if not valid:
            return False, msg

        # 2. Positive Check: JS 키워드가 있는가?
        js_keywords = [
            r"\bfunction\b",
            r"\bconst\b",
            r"\blet\b",
            r"=>",
            r"\bconsole\.log\b",
            r"\bwindow\.",
            r"\bdocument\.",
        ]
        if not any(re.search(k, code) for k in js_keywords):
            return (
                False,
                "유효한 JavaScript 코드가 아닌 것 같습니다. (함수나 변수 선언이 필요합니다)",
            )

        return True, ""

    def get_system_instruction(self) -> str:
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
        return "const add = (a, b) => {\n  return a + b;\n};"

    def get_syntax_name(self) -> str:
        return "javascript"
