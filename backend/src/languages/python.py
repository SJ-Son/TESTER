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
1. **[Extreme Pure Code]**: 어떠한 설명, 주석, 가이드라인도 출력하지 마십시오. 오직 실행 가능한 테스트 코드만 출력합니다.
2. `import pytest` 등 필수 라이브러리 import만 포함합니다.
3. 원본 함수나 클래스의 재정의나 "import 가이드 주석"조차 출력하지 마십시오.
4. 테스트 함수 내부의 한글 주석도 모두 제거하고, 함수 이름만으로 의도를 전달하십시오.
5. 오직 `pytest` 기반의 순수 테스트 로직만 코드 블록으로 출력합니다.

[출력 형식]
- **[CRITICAL]**: 마크다운 코드 블록(```python ... ```)을 절대 사용하지 마십시오.
- 어떠한 마크다운 형식도 없이 오직 순수한 원본 코드(Raw Text)만 출력합니다.
- 예: import pytest ... (백틱 없이 바로 시작)
"""

    def get_placeholder(self) -> str:
        return "def add(a, b):\n    return a + b"

    def get_syntax_name(self) -> str:
        return "python"
