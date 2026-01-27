# 🧪 Code Tester AI

파이썬 코드를 입력하면 Google Gemini AI가 자동으로 완벽한 테스트 코드(Unit Test)를 작성해주는 Streamlit 애플리케이션입니다.

## 📌 주요 기능
- **자동 테스트 생성:** 코드 분석 후 `pytest` 또는 `unittest` 기반 테스트 코드 작성.
- **모델 선택:** `gemini-1.5-flash` (빠름)와 `gemini-1.5-pro` (정확함) 모델 전환 가능.
- **최적화:** 동일한 요청에 대해 캐싱(Caching)을 적용하여 비용 절감 및 속도 향상.
- **UI:** 직관적인 Split View (입력/출력) 제공.

## 📂 프로젝트 구조 (Project Structure)
```
.
├── .env.example            # 환경 변수 예제
├── .gitignore              # Git 무시 설정
├── README.md               # 프로젝트 문서
├── pytest.ini              # Pytest 설정
├── requirements.txt        # 의존성 목록
├── run.py                  # 실행 스크립트
├── src/
│   ├── app.py              # 메인 UI (Streamlit)
│   ├── config/
│   │   └── settings.py     # 환경 설정 관리
│   ├── services/
│   │   └── gemini_service.py # Gemini API 서비스 로직
│   └── utils/
│       ├── logger.py       # 로깅 유틸리티
│       └── prompts.py      # 시스템 프롬프트 관리
└── tests/
    └── test_gemini.py      # 단위 테스트 (Mock 적용)
```

## 🚀 시작하기 (Getting Started)

### 1. 초기 설정
필요한 라이브러리를 설치합니다.
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정
`.env.example` 파일을 복사하여 `.env` 파일을 생성하고, Google Gemini API Key를 입력하세요.
```bash
cp .env.example .env
# .env 파일 편집 (GEMINI_API_KEY 입력)
```

### 3. 애플리케이션 실행
다음 명령어로 앱을 실행하세요.
```bash
streamlit run run.py
```
브라우저에서 `http://localhost:8501`이 자동으로 열립니다.

## ✅ 테스트 (Testing)
비용 발생을 막기 위해 Mocking된 단위 테스트를 실행할 수 있습니다.
```bash
pytest tests/
```

## 🛠 기술 스택
- **Language:** Python 3.11+
- **Framework:** Streamlit
- **AI Model:** Google Gemini 1.5 (via `google-generativeai`)
- **Testing:** Pytest, Pytest-Mock
