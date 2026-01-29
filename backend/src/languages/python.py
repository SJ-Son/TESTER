import ast
from backend.src.languages.base import LanguageStrategy

class PythonStrategy(LanguageStrategy):
    def validate_code(self, code: str) -> tuple[bool, str]:
        if not code.strip():
            return False, "코드를 입력해주세요."
        
        try:
            ast.parse(code)
            return True, ""
        except SyntaxError:
            return False, "유효한 파이썬 코드가 아닙니다."

    def get_system_instruction(self) -> str:
        return """
당신은 Google의 전문 QA 엔지니어입니다.
사용자가 입력한 파이썬 코드를 분석하여 테스트 코드를 작성합니다.

[핵심 가이드라인]
1. **[Raw Code]**: 마크다운 코드 블록(백틱)을 절대 사용하지 마십시오. 오직 순수 텍스트만 출력합니다.
2. 원본 함수의 재정의나 외부 Import 가이드 주석은 출력하지 마십시오.
3. **[Balanced Comments]**: 각 테스트 함수 내부에는 무엇을 검증하는지 설명하는 간단한 한 줄 주석을 포함하십시오. (예: `# 정상 범위 입력 테스트`)
4. 전체적인 설명이나 부연 설명은 여전히 금지하며, 오직 코드와 내부의 최소한의 주석만 출력합니다.
5. 오직 `pytest` 기반의 순수 테스트 로직만 출력합니다.

[출력 형식]
- **[CRITICAL]**: 마크다운 코드 블록(```python ... ```)을 절대 사용하지 마십시오.
- 어떠한 마크다운 형식도 없이 오직 순수한 원본 코드(Raw Text)만 출력합니다.
- 예: import pytest ... (백틱 없이 바로 시작)
"""

    def get_placeholder(self) -> str:
        return "def add(a, b):\n    return a + b"

    def get_syntax_name(self) -> str:
        return "python"
