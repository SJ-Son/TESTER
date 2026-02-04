# Language Strategy Pattern

## 개요

언어별 테스트 코드 생성 전략을 캡슐화한 모듈입니다. **Strategy Pattern**과 **Factory Pattern**을 조합하여 확장 가능한 구조를 제공합니다.

## 디자인 패턴

### Strategy Pattern
각 언어(Python, JavaScript, Java)는 공통 인터페이스(`LanguageStrategy`)를 구현합니다.

```python
# base.py
from abc import ABC, abstractmethod

class LanguageStrategy(ABC):
    @abstractmethod
    def validate_code(self, code: str) -> tuple[bool, str]:
        """코드 검증 (문법, 보안 체크)"""
        pass
    
    @abstractmethod
    def get_system_instruction(self) -> str:
        """AI에게 전달할 언어별 시스템 프롬프트"""
        pass
```

### Factory Pattern
`LanguageFactory`가 언어에 맞는 전략 객체를 생성합니다 (Singleton).

```python
# factory.py
class LanguageFactory:
    _strategy_classes = {
        "python": PythonStrategy,
        "javascript": JavaScriptStrategy,
        "java": JavaStrategy,
    }
    _instances = {}  # 캐싱
    
    @classmethod
    def get_strategy(cls, language: str) -> LanguageStrategy:
        if language in cls._instances:
            return cls._instances[language]  # 재사용
        
        cls._instances[language] = cls._strategy_classes[language]()
        return cls._instances[language]
```

---

## 구현된 전략

### 1. **PythonStrategy**

**검증 로직:**
- 빈 코드 확인
- 위험 키워드 체크: `eval`, `exec`, `compile`, `__import__`
- 최소 길이: 10자
- 최대 길이: 100,000자

**시스템 프롬프트:**
```
You are a senior Python test engineer using pytest.
Generate comprehensive test cases following best practices:
- Use pytest fixtures and parametrize
- Include edge cases and error handling
- Follow PEP 8 style guide
...
```

### 2. **JavaScriptStrategy**

**검증 로직:**
- Python과 유사하지만 JS 특화 위험 키워드 추가

**시스템 프롬프트:**
```
You are a senior JavaScript test engineer using Jest/Mocha.
Generate comprehensive test cases:
- Use describe/it blocks
- Mock external dependencies
- Test async/await properly
...
```

### 3. **JavaStrategy**

**검증 로직:**
- Java 특화 위험 패턴 체크

**시스템 프롬프트:**
```
You are a senior Java test engineer using JUnit 5.
Generate comprehensive test cases:
- Use @Test annotations
- Follow AAA pattern (Arrange-Act-Assert)
- Use Mockito for mocking
...
```

---

## 새 언어 추가하기

### Step 1: Strategy 클래스 작성

```python
# languages/typescript.py
from backend.src.languages.base import LanguageStrategy

class TypeScriptStrategy(LanguageStrategy):
    def validate_code(self, code: str) -> tuple[bool, str]:
        if not code.strip():
            return False, "코드가 비어있습니다"
        
        dangerous_patterns = ["eval(", "Function("]
        for pattern in dangerous_patterns:
            if pattern in code:
                return False, f"위험한 패턴 감지: {pattern}"
        
        return True, ""
    
    def get_system_instruction(self) -> str:
        return """
        You are a TypeScript test engineer using Jest.
        Generate type-safe test cases with proper type assertions.
        """
```

### Step 2: Factory에 등록

```python
# languages/factory.py
from backend.src.languages.typescript import TypeScriptStrategy

class LanguageFactory:
    _strategy_classes = {
        "python": PythonStrategy,
        "javascript": JavaScriptStrategy,
        "java": JavaStrategy,
        "typescript": TypeScriptStrategy,  # 추가
    }
```

### Step 3: 프론트엔드 업데이트

```typescript
// frontend/src/components/ControlPanel.vue
const languages = [
  { value: 'python', label: 'Python' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'java', label: 'Java' },
  { value: 'typescript', label: 'TypeScript' }  // 추가
]
```

---

## 검증 로직 설계 원칙

### 1. **보안 우선**
위험한 코드 실행 방지를 최우선으로 합니다.

```python
DANGEROUS_KEYWORDS = [
    "eval", "exec", "compile",    # Python 동적 실행
    "__import__",                 # 임의 모듈 import
    "subprocess", "os.system"     # 시스템 명령 실행
]
```

### 2. **빠른 실패 (Fail Fast)**
문제가 있으면 즉시 에러 반환 (API 비용 절약).

```python
if len(code) > 100000:
    return False, "코드가 너무 깁니다 (최대 100,000자)"
```

### 3. **명확한 에러 메시지**
사용자가 무엇을 고쳐야 하는지 알 수 있도록.

```python
return False, f"위험한 키워드 감지: '{keyword}' 사용 불가"
```

---

## 시스템 프롬프트 작성 가이드

### 좋은 프롬프트의 조건:
1. **역할 명시:** "You are a senior {언어} test engineer"
2. **프레임워크 지정:** "using pytest", "using Jest"
3. **코드 스타일:** "Follow PEP 8", "Use AAA pattern"
4. **커버리지 요구:** "Include edge cases", "Test error handling"
5. **출력 형식:** "Only return test code", "No explanations"

### 예시 (Python):
```python
def get_system_instruction(self) -> str:
    return """
You are a senior Python test engineer using pytest.

Requirements:
1. Generate comprehensive test cases covering:
   - Happy path scenarios
   - Edge cases (None, empty, large inputs)
   - Error handling (exceptions)
   
2. Best practices:
   - Use pytest fixtures for setup/teardown
   - Use @pytest.mark.parametrize for multiple cases
   - Follow AAA pattern (Arrange-Act-Assert)
   - Include docstrings
   
3. Code style:
   - Follow PEP 8
   - Use descriptive test names (test_function_name_scenario)
   - Keep tests isolated (no shared state)
   
4. Output format:
   - Only return executable test code
   - No explanations or markdown formatting
   - Include necessary imports
    """.strip()
```

---

## 테스트 예시

```python
# tests/languages/test_python_strategy.py
import pytest
from backend.src.languages.python import PythonStrategy

def test_validate_empty_code():
    strategy = PythonStrategy()
    is_valid, msg = strategy.validate_code("")
    
    assert not is_valid
    assert "비어있습니다" in msg

def test_validate_dangerous_keyword():
    strategy = PythonStrategy()
    code = "eval('print(1)')"
    is_valid, msg = strategy.validate_code(code)
    
    assert not is_valid
    assert "eval" in msg

def test_get_system_instruction():
    strategy = PythonStrategy()
    instruction = strategy.get_system_instruction()
    
    assert "pytest" in instruction
    assert "senior" in instruction
```

---

## 성능 최적화

### Singleton Pattern
전략 객체는 한 번만 생성되어 재사용됩니다.

```python
# 첫 요청
strategy = LanguageFactory.get_strategy("python")  # 새로 생성

# 두 번째 요청
strategy = LanguageFactory.get_strategy("python")  # 캐시에서 반환
```

**장점:** 메모리 절약, 인스턴스 생성 오버헤드 제거

---

## 확장 아이디어

### 1. **동적 프롬프트 생성**
사용자 선호도에 따라 프롬프트 커스터마이징

```python
def get_system_instruction(self, style: str = "standard") -> str:
    if style == "minimal":
        return "Generate minimal test cases..."
    elif style == "comprehensive":
        return "Generate exhaustive test suite..."
```

### 2. **검증 규칙 외부화**
YAML/JSON 파일로 규칙 관리

```yaml
# languages/rules/python.yaml
dangerous_keywords:
  - eval
  - exec
max_length: 100000
min_length: 10
```

### 3. **Multi-version 지원**
Python 2 vs 3, Java 8 vs 17 등

```python
class PythonStrategy:
    def __init__(self, version: str = "3"):
        self.version = version
```
