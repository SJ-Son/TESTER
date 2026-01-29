import re
from backend.src.languages.base import LanguageStrategy

class JavaScriptStrategy(LanguageStrategy):
    def validate_code(self, code: str) -> tuple[bool, str]:
        if not code.strip():
            return False, "코드를 입력해주세요."
        
        # 1. Negative Check: 다른 언어(Python, Java 등)의 강력한 특징이 있는가?
        # - Python: def 키워드 (JS에는 없으므로), import ... from ... (JS는 import ... from '...' 따옴표 필수지만 regex로 구분 힘듬, :로 끝나는 블록 등)
        # - Java: public static void, String[] args, System.out.println
        
        # Python 의심 패턴
        if re.search(r'^\s*def\s+\w+\s*\(.*\)\s*:', code, re.MULTILINE):
            return False, "Python 코드로 감지됩니다. 언어 설정을 'Python'으로 변경해주세요."
        if re.search(r'^\s*import\s+.*\s+from\s+', code, re.MULTILINE) and not re.search(r"['\"]", code): # 따옴표 없는 import (Python style)
             return False, "Python 코드로 감지됩니다. (Import 구문)"

        # Java 의심 패턴
        if re.search(r'\bpublic\s+static\s+void\b', code):
            return False, "Java 코드로 감지됩니다. 언어 설정을 'Java'로 변경해주세요."
        if re.search(r'\bSystem\.out\.println\b', code):
             return False, "Java 코드로 감지됩니다."

        # 2. Positive Check: JS 키워드가 있는가?
        js_keywords = [r'\bfunction\b', r'\bconst\b', r'\blet\b', r'\bvar\b', r'=>', r'\bclass\b', r'\bconsole\.log\b']
        if not any(re.search(k, code) for k in js_keywords):
            return False, "유효한 JavaScript 코드가 아닌 것 같습니다. (함수나 변수 선언이 필요합니다)"

        return True, ""

    def get_system_instruction(self) -> str:
        return """
당신은 Google의 전문 JavaScript QA 엔지니어입니다.
사용자가 입력한 자바스크립트 코드를 분석하여 `Jest` 테스트 코드를 작성합니다.

[핵심 가이드라인]
1. **[Extreme Pure Code]**: 어떠한 설명, 주석, 가이드라인도 출력하지 마십시오. 오직 실행 가능한 테스트 코드만 출력합니다.
2. 원본 함수나 클래스의 재정의나 "import 가이드 주석"조차 출력하지 마십시오.
3. 테스트 함수 내부의 설명 주석을 모두 제거하십시오.
4. 모듈 시스템(CommonJS/ESM)은 입력 코드와 일치시킵니다.
5. 오직 `Jest` 기반의 순수 테스트 로직만 코드 블록으로 출력합니다.

[출력 형식]
- **[CRITICAL]**: 마크다운 코드 블록(```javascript ... ```)을 절대 사용하지 마십시오.
- 어떠한 마크다운 형식도 없이 오직 순수한 원본 코드(Raw Text)만 출력합니다.
- 예: import { ... } from ... (백틱 없이 바로 시작)
"""

    def get_placeholder(self) -> str:
        return "const add = (a, b) => {\n  return a + b;\n};"
    
    def get_syntax_name(self) -> str:
        return "javascript"
