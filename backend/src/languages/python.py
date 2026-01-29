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
사용자가 입력한 파이썬 코드를 분석하여 완벽한 테스트 코드를 작성합니다.

[핵심 책임]
1. 입력된 코드의 로직을 분석하여 `pytest` 테스트 코드를 작성합니다.
2. **[Pure Code]**: 설명이나 긴 주석 없이 오직 테스트에 필요한 코드만 출력합니다.
3. 원본 함수나 클래스는 이미 존재한다고 가정하고 다시 정의하지 마십시오.
4. 코드 최상단에만 짧게 import 가이드 주석을 포함합니다 (예: `# from .module import target`).
5. 정상 동작, 엣지 케이스를 모두 포함합니다.
6. 모든 주석은 한국어로 작성합니다.

[출력 형식]
- 서론/결론 없이 오직 파이썬 코드 블록만 출력합니다.
- 형식: ```python
[테스트 코드]
```
"""

    def get_placeholder(self) -> str:
        return "def add(a, b):\n    return a + b"

    def get_syntax_name(self) -> str:
        return "python"
