import re
from backend.src.languages.base import LanguageStrategy

class JavaStrategy(LanguageStrategy):
    def validate_code(self, code: str) -> tuple[bool, str]:
        if not code.strip():
            return False, "코드를 입력해주세요."
            
        # 1. Negative Check
        # Python 의심
        if re.search(r'^\s*def\s+\w+\s*\(.*\)\s*:', code, re.MULTILINE):
            return False, "Python 코드로 감지됩니다. 언어 설정을 'Python'으로 변경해주세요."
        # JS 의심
        if re.search(r'\bconsole\.log\b', code):
            return False, "JavaScript 코드로 감지됩니다. 언어 설정을 'JavaScript'로 변경해주세요."
        if re.search(r'\bfunction\s+\w+\s*\(', code):
            return False, "JavaScript 코드로 감지됩니다."
        if "=>" in code and not "->" in code: # JS Arrow function vs Java Lambda (Java uses ->)
            # 화살표가 있다고 무조건 JS는 아니지만, => 가 있고 class가 없으면 강한 의심
            pass 

        # 2. Positive Check: Java 키워드
        java_keywords = [r'\bclass\b', r'\binterface\b', r'\bpublic\b', r'\bprivate\b', r'\bprotected\b', r'@Override']
        if not any(re.search(k, code) for k in java_keywords):
            return False, "유효한 Java 코드가 아닌 것 같습니다. (class 정의 또는 접근 제어자가 필요합니다)" 

        return True, ""

    def get_system_instruction(self) -> str:
        return """
당신은 Google의 전문 Java QA 엔지니어입니다.
사용자가 입력한 Java 코드를 분석하여 완벽한 `JUnit 5` 테스트 클래스를 작성합니다.

[핵심 책임]
1. 입력된 코드의 구조를 분석하여 `JUnit 5` 및 `Mockito` 기반 테스트를 작성합니다.
2. **[Pure Code]**: 오직 테스트 클래스와 필요한 import만 출력합니다. 원본 클래스는 이미 존재한다고 가정합니다.
3. 코드 최상단에 짧게 import 가이드 주석을 포함합니다 (예: `// import your.TargetClass`).
4. **[No Package]**: 바로 사용할 수 있도록 `package` 선언은 생략합니다.
5. 모든 주석은 한국어로 작성합니다.

[출력 형식]
- 서론/결론 없이 오직 Java 코드 블록만 출력합니다.
- 형식: ```java
[테스트 코드]
```
"""

    def get_placeholder(self) -> str:
        return "public class Calculator {\n    public int add(int a, int b) {\n        return a + b;\n    }\n}"

    def get_syntax_name(self) -> str:
        return "java"
