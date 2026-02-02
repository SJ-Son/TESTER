# TESTER

<div align="center">
  <img src="https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D" alt="Vue.js" />
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
</div>

**TESTER**는 FastAPI와 Vue 3로 구성된 웹 애플리케이션입니다. Google Generative AI를 이용한 콘텐츠 생성 및 인증 시스템을 포함합니다.

---

## ✨ 주요 기능 (Key Features)

*   ✨ **AI 콘텐츠 생성**: Google Generative AI(Gemini) 연동 텍스트/콘텐츠 생성
*   🚀 **API 서버**: Python FastAPI 기반 비동기 백엔드 구성
*   🎨 **UI**: Vue 3, TypeScript, TailwindCSS 기반 인터페이스
*   🔐 **인증**: JWT 및 Google OAuth 기반 사용자 인증
*   🛡️ **신뢰**: 소스 코드 **비저장(RAM-only)** 및 즉시 파기 정책
*   📜 **법적 고지**: 이용약관 및 개인정보처리방침 페이지 (`/terms`, `/privacy`)
*   📦 **인프라**: Docker 컨테이너 및 Firebase Hosting 배포 환경

---

## 🛠 기술 스택 (Tech Stack)

| 분류 | 기술 |
| :--- | :--- |
| **Backend** | Python 3.9+, FastAPI, Uvicorn, SQLAlchemy (or similar), Google GenAI SDK |
| **Frontend** | Vue 3, TypeScript, Vite, Pinia, TailwindCSS, Lucide Icons |
| **Testing** | Pytest, Pytest-Mock |
| **DevOps** | Docker, Firebase Hosting |

---

## 🚀 로컬 개발 환경 설정 (Local Development Setup)

이 프로젝트를 로컬 개발 환경에서 실행하거나 기여하고 싶은 개발자를 위한 가이드입니다.

### 1. 사전 요구사항 (Prerequisites)

*   **Node.js** (v18 이상 권장)
*   **Python** (3.9 이상 권장)
*   **Git**

### 2. 프로젝트 클론 (Clone)

```bash
git clone https://github.com/your-username/TESTER.git
cd TESTER
```

### 3. 백엔드 설정 및 실행 (Backend)

백엔드 서버는 `localhost:8000`에서 실행됩니다.

```bash
cd backend

# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 필수 API Key를 입력하세요:
# - GEMINI_API_KEY
# - GOOGLE_CLIENT_ID & SECRET
# - RECAPTCHA_SECRET_KEY

# 서버 실행
uvicorn src.main:app --reload
```

### 4. 프론트엔드 설정 및 실행 (Frontend)

프론트엔드 개발 서버는 `localhost:5173`에서 실행됩니다.

```bash
cd frontend

# 의존성 설치
npm install

# 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 필수 키를 입력하세요:
# - VITE_GOOGLE_CLIENT_ID
# - VITE_RECAPTCHA_SITE_KEY

# 개발 서버 실행
npm run dev
```

브라우저에서 `http://localhost:5173`으로 접속하여 애플리케이션을 확인하세요.

---

## 📂 폴더 구조 (Folder Structure)

```text
TESTER/
├── backend/
│   ├── src/
│   │   ├── api/              # API 엔드포인트 (모듈화)
│   │   │   ├── v1/           # API v1
│   │   │   │   ├── auth.py       # 인증 엔드포인트
│   │   │   │   ├── generator.py  # 코드 생성 엔드포인트
│   │   │   │   ├── health.py     # 헬스 체크
│   │   │   │   └── deps.py       # 공유 의존성
│   │   │   └── routers.py    # 라우터 통합
│   │   ├── config/           # 환경 변수 및 앱 설정
│   │   ├── services/         # 비즈니스 로직 (Gemini, Language)
│   │   ├── exceptions.py     # 커스텀 예외 타입
│   │   ├── auth.py           # 인증 유틸리티
│   │   └── main.py           # FastAPI 앱 진입점 (미들웨어)
│   ├── tests/                # Pytest 테스트 코드
│   ├── requirements.txt      # 백엔드 의존성 목록
│   └── .env.example          # 환경 변수 예시
│
├── frontend/
│   ├── src/
│   │   ├── api/              # API 통신 레이어
│   │   │   ├── auth.ts           # 인증 API
│   │   │   ├── generator.ts      # 코드 생성 API
│   │   │   └── types.ts          # API 타입 정의
│   │   ├── components/       # 재사용 가능한 UI 컴포넌트
│   │   ├── views/            # 페이지 뷰 (Home, Legal, Changelog)
│   │   ├── router/           # Vue Router 설정
│   │   ├── stores/           # Pinia 상태 관리 (비즈니스 로직)
│   │   └── ...
│   ├── package.json          # 프론트엔드 의존성 목록
│   └── vite.config.ts        # Vite 빌드 설정
│
├── pyproject.toml            # Ruff 린팅 설정
├── .pre-commit-config.yaml   # Git pre-commit 훅 설정
├── firebase.json             # Firebase 배포 설정
├── Dockerfile                # 도커 이미지 빌드 설정
└── README.md                 # 프로젝트 설명서
```

---

## 🔧 코드 품질 (Code Quality)

이 프로젝트는 일관된 코드 스타일과 높은 품질을 유지하기 위해 자동화된 도구를 사용합니다.

### Linting & Formatting

*   **Ruff**: Python 코드 린팅 및 포맷팅 (Black, Flake8, isort 대체)
*   **Pre-commit Hooks**: 커밋 전 자동 코드 품질 검사

```bash
# 린팅 실행
ruff check backend/src/

# 자동 포맷팅
ruff format backend/src/

# Pre-commit 훅 설치 (최초 1회)
pre-commit install
```

---

## 📖 API 문서 (API Documentation)

백엔드 서버가 실행 중일 때, 다음 주소에서 자동으로 생성된 API 문서를 확인할 수 있습니다.

*   **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
*   **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🔖 버전 관리 (Versioning)

상세 변경 이력은 [CHANGELOG.md](./CHANGELOG.md)에서 확인할 수 있습니다.

*   **Major**: 호환되지 않는 API 변경
*   **Minor**: 하위 호환성 있는 기능 추가
*   **Patch**: 하위 호환성 있는 버그 수정

---
## 🚀 Roadmap (TODO)

### 📂 Phase 2: Persistence & Engineering Foundation
- [ ] **Intelligent DB Schema**: 단순 저장을 넘어 요소 식별용 벡터 데이터(Locator)를 포함한 Supabase 스키마 구축
- [ ] **Project-based Workspace**: 히스토리를 넘어 프로젝트 단위의 테스트 케이스 관리 및 버전 제어 인터페이스 구현
- [ ] **AI-Ready Backend**: 생성된 코드가 즉시 DB에 영속화되고 실행 준비 상태가 되는 데이터 파이프라인 개편

### ⚡ Phase 3: Intelligent Execution & Sandbox
- [ ] **Pre-warmed Sandbox**: Cloud Run Jobs 기반 격리 환경 구축
- [ ] **Self-Healing Loop**: 실행 결과(Trace)를 AI가 분석하여 코드를 자동 수정하는 자가 치유 피드백 루프 구현
- [ ] **Visual Debugger**: 실시간 로그 스트리밍 및 픽셀 단위 Visual Regression 리포팅 대시보드 개발
---

## 📄 라이선스 (License)

이 프로젝트의 소스 코드는 MIT 라이선스 하에 배포됩니다.
