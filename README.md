# Python QA Test Generator

## 1. 프로젝트 개요
Python 소스 코드를 입력받아 Google Gemini API를 이용해 `pytest` 기반의 단위 테스트 코드를 생성하는 웹 애플리케이션입니다.

## 2. 주요 기능
- **Streamlit 기반 웹 인터페이스**
- **Google Gemini API 연동**: `gemini-3-flash-preview` 등 모델 선택 및 테스트 코드 생성
- **실시간 스트리밍 응답**: 생성되는 코드를 실시간으로 출력 (Streaming)
- **입력 코드 검증**: Python AST(Abstract Syntax Tree)를 활용한 문법 유효성 검사
- **API 호출 제어**: `Tenacity`를 이용한 재시도(Retry) 로직 및 간단한 속도 제한(Rate Limit) 구현

## 3. 기술 스택
- **Python**: 3.12.1
- **Web App**: Streamlit
- **LLM**: Google Generative AI SDK (Gemini)
- **Testing**: Pytest, Pytest-Mock
- **Utils**: Tenacity (Retry), Python-Dotenv (Env vars)

## 4. 프로젝트 구조
```
.
├── run.py                  # 애플리케이션 진입점 (Launcher)
├── src/
│   ├── app.py              # 메인 UI 및 로직
│   ├── config/
│   │   └── settings.py     # 환경 변수 및 설정 관리
│   ├── services/
│   │   └── gemini_service.py # Gemini API 호출 서비스
│   └── utils/
│       ├── logger.py       # 로깅 설정
│       └── prompts.py      # LLM 시스템 프롬프트
├── tests/                  # 단위 테스트 코드
├── requirements.txt        # 의존성 패키지 목록
└── .env                    # 환경 변수 (비공개)
```

## 5. 설치 및 실행

### 가상환경 및 패키지 설치
MacOS/Linux 환경 기준:

```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# 패키지 설치
pip3 install -r requirements.txt
```

### 환경 변수 설정
`.env` 파일을 생성하고 API 키를 설정합니다.

```ini
GEMINI_API_KEY=your_api_key
```

### 실행
```bash
# 로컬 실행
python3 run.py
```
