# Language Strategy 메모

언어별 생성 전략을 캡슐화함.
Strategy Pattern + Factory Pattern 조합.

## 구조 (Design Pattern)

### Strategy
- `LanguageStrategy` (추상 클래스) 상속받아서 구현.
- `validate_code()`: 문법/보안 검사.
- `get_system_instruction()`: AI한테 줄 프롬프트 생성.

### Factory
- `LanguageFactory`: 언어 문자열(python, javascript 등) 받아서 맞는 Strategy 객체 줌.
- Singleton으로 구현해서 객체 재사용함 (메모리 절약).

## 구현체별 특징

### PythonStrategy
- 검증: `eval`, `exec` 같은 위험 키워드 막음.
- 프롬프트: `pytest` 사용하라고 시킴.

### JavaScriptStrategy
- 프롬프트: `Jest` 사용하라고 시킴.

### JavaStrategy
- 프롬프트: `JUnit 5` 사용하라고 시킴.

## 확장 방법 (새 언어 추가)
1. `languages/새언어.py` 만들고 `LanguageStrategy` 상속 구현.
2. `languages/factory.py` 딕셔너리에 등록.
3. 프론트엔드 셀렉트 박스에 옵션 추가.

## 보안 원칙 (Security)
- Blacklist 방식 키워드 필터링 사용 (완벽하진 않지만 1차 방어선).
- 너무 긴 코드(10만자 이상)는 API 비용 문제로 거절.
