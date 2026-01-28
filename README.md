# QA Test Code Generator (V3: Agentic Workflow)

Python, Java, JavaScript 소스 코드를 입력받아 Google Gemini API를 이용해 완벽한 단위 테스트 코드를 생성하는 **Agentic AI 애플리케이션**입니다.

## 🚀 주요 기능 (Key Features)

### 1. Multi-Language Support (V2)
- **Python**: `pytest` 기반 테스트 생성 (AST 문법 검증)
- **Java**: `JUnit 5` + `Mockito` 기반 테스트 생성 (Cross-Validation)
- **JavaScript**: `Jest` 기반 테스트 생성 (Module System 감지)
- **Strategy Pattern**: 확장 가능한 아키텍처로 설계되어 새로운 언어 추가가 용이함

### 2. Agentic Workflow (V3)
- **The Self-Corrector (자기 성찰 루프)**
    - AI가 생성한 초안(Draft)을 스스로 검토하고 수정합니다.
    - 문법 오류나 언어 혼용 실수를 잡아냅니다.
    - UI 사이드바의 **"Enable Self-Correction"** 옵션으로 활성화 가능.
- **The Teacher (자동 평가 시스템)**
    - `tests/auto_evaluator.py`를 통해 AI의 성능을 정량적으로 평가합니다.
    - Python/Java/JS가 섞인 함정 코드를 100% 걸러냅니다.

### 3. Core Features
- **Streamlit Web UI**: 직관적인 언어 선택 및 옵션 제어
- **Real-time Streaming**: 생성되는 코드를 실시간으로 확인
- **Robustness**: 입력 코드의 언어가 맞지 않으면 즉시 차단 (Negative Check)

---

## 🛠️ 기술 스택 (Tech Stack)
- **Language**: Python 3.12+
- **Framework**: Streamlit
- **LLM**: Google Generative AI (Gemini-1.5/2.0/3.0)
- **Design Pattern**: Strategy Pattern, Factory Pattern
- **Testing**: Pytest, Pytest-Mock
- **Utils**: Tenacity (Retry), Python-Dotenv

---

## 📂 프로젝트 구조

```bash
.
├── run.py                  # 애플리케이션 런처
├── src/
│   ├── app.py              # 메인 UI (Streamlit)
│   ├── languages/          # 언어별 전략 (Strategy Pattern)
│   │   ├── base.py         # Strategy Interface
│   │   ├── factory.py      # Language Factory
│   │   ├── python.py       # Python Strategy
│   │   ├── java.py         # Java Strategy
│   │   └── javascript.py   # JavaScript Strategy
│   └── services/
│       └── gemini_service.py # LLM Service (Reflection Loop 포함)
├── tests/
│   ├── auto_evaluator.py         # [V3] 자동 평가 스크립트 (The Teacher)
│   ├── verify_reflection_effect.py # [V3] Self-Correction 효과 검증 (A/B Test)
│   └── test_v2_languages.py      # 언어별 검증 로직 테스트
└── requirements.txt
```

---

## ⚡ 설치 및 실행

### 1. 환경 설정
```bash
# 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. API 키 설정
`.env` 파일을 생성하고 Google AI Studio에서 발급받은 키를 입력하세요.
```ini
GEMINI_API_KEY=your_api_key_here
```

### 3. 애플리케이션 실행
```bash
python3 run.py
# 또는
streamlit run src/app.py
```

---

## 🧪 검증 및 테스트 (Verification)

### 자동 평가 (Auto Evaluator) 실행
AI가 함정 코드(Trap Cases)를 잘 통과하는지 채점합니다.
```bash
python3 tests/auto_evaluator.py
```

### Self-Correction 효과 검증 (A/B Test)
Reflection 옵션 유무에 따른 코드 품질 차이를 비교합니다.
```bash
python3 tests/verify_reflection_effect.py
```

### 단위 테스트 실행
```bash
pytest
```
