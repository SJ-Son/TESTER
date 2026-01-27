# Python QA Test Generator

## 1. 개요
Python 소스 코드를 입력받아 Google Gemini API를 통해 `pytest` 기반의 단위 테스트 코드를 자동 생성하는 Streamlit 애플리케이션이다. AST 기반으로 입력 코드를 검증하며, 생성된 테스트 코드는 즉시 실행 가능한 형태로 제공된다.

## 2. 기술 스택
- **Language**: Python 3.10+
- **Framework**: Streamlit
- **AI Model**: Google Generative AI (Gemini 1.5 Flash/Pro)
- **Validation**: AST (Abstract Syntax Tree)
- **Testing**: Pytest

## 3. 설치 및 실행 (Installation)

### 가상환경 생성 및 패키지 설치
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Mac/Linux)
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 실행
```bash
# 로컬 실행
python run.py

# 또는 Streamlit 실행
streamlit run run.py
```

## 4. 환경 변수 설정 (.env)
프로젝트 루트 경로에 `.env` 파일을 생성하고 아래 내용을 추가한다.

```ini
GEMINI_API_KEY=your_api_key_here
```

- `GEMINI_API_KEY`: Google AI Studio에서 발급받은 API Key.

## 5. 테스트 실행
프로젝트의 단위 테스트를 수행한다.

```bash
pytest tests/
```

## 6. 프로젝트 구조 (Project Structure)
```
.
├── run.py                  # 애플리케이션 진입점
├── src/
│   ├── app.py              # Main UI 및 애플리케이션 로직
│   ├── config/
│   │   └── settings.py     # 환경 변수 및 설정 관리
│   ├── services/
│   │   └── gemini_service.py # Gemini API 연동 및 비즈니스 로직
│   └── utils/
│       ├── logger.py       # 로깅 유틸리티
│       └── prompts.py      # 시스템 프롬프트 정의
├── tests/                  # 테스트 코드 디렉토리
├── requirements.txt        # 의존성 패키지 목록
├── .env                    # 환경 변수 설정 파일 (git ignored)
└── README.md               # 프로젝트 문서
```
