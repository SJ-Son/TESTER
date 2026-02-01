# TESTER

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)
[![Live Demo](https://img.shields.io/badge/demo-live-red)](https://gen-lang-client-0355642569.web.app)

**TESTER**는 FastAPI와 Vue 3로 구성된 웹 애플리케이션입니다. Google Generative AI를 이용한 콘텐츠 생성 및 인증 시스템을 포함합니다.

---

## ✨ 주요 기능 (Key Features)

*   ✨ **AI 콘텐츠 생성**: Google Generative AI(Gemini) 연동 텍스트/콘텐츠 생성
*   🚀 **API 서버**: Python FastAPI 기반 비동기 백엔드 구성
*   🎨 **UI**: Vue 3, TypeScript, TailwindCSS 기반 인터페이스
*   🔐 **인증**: JWT 및 Google OAuth 기반 사용자 인증
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
│   │   ├── config/       # 환경 변수 및 앱 설정
│   │   ├── services/     # 비즈니스 로직
│   │   ├── main.py       # FastAPI 앱 진입점
│   │   └── ...
│   ├── tests/            # Pytest 테스트 코드
│   ├── requirements.txt  # 백엔드 의존성 목록
│   └── .env.example      # 환경 변수 예시
│
├── frontend/
│   ├── src/
│   │   ├── components/   # 재사용 가능한 UI 컴포넌트
│   │   ├── views/        # 페이지 뷰
│   │   ├── stores/       # Pinia 상태 관리
│   │   └── ...
│   ├── package.json      # 프론트엔드 의존성 목록
│   └── vite.config.ts    # Vite 빌드 설정
│
├── firebase.json         # Firebase 배포 설정
├── Dockerfile            # 도커 이미지 빌드 설정
└── README.md             # 프로젝트 설명서
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
## TODO
### 🏗️ 로드맵

#### 🥇 Phase 1: 구조 및 규칙 확립 (Foundation)
*   [ ] **Backend Router Split**: `main.py`의 엔드포인트를 `api/v1/{auth, generator, users}.py`로 도메인별 분리 (확장성 확보)
*   [ ] **Linting & Formatting**: `ruff` 및 `pre-commit` 훅 적용 (코드 스타일 통일 및 자동화)

#### 🥈 Phase 2: 안정성 및 사용자 경험 (Stability)
*   [ ] **SSE 에러 핸들링 표준화**: `event: message` vs `event: error` 분리 및 명확한 에러 원인 전달
*   [ ] **Frontend API Layer**: Store 내 `fetch` 로직을 `src/api/` 서비스 모듈로 격리 (유지보수성)
*   [ ] **Exception Handling**: 포괄적 예외 처리(`except Exception`) 지양 및 구체적 에러 정의

#### 🥉 Phase 3: 최적화 및 고도화 (Optimization)
*   [ ] **같은질문 다른대답 (Caching)**: 동일 요청에 대한 캐싱 로직 고도화 (비용 절감)
*   [ ] **Structured Logging**: JSON 포맷 로깅 도입 및 Request ID 추적 (관측 가능성)
*   [ ] **Strict Typing**: `mypy` 도입 및 타입 힌트 강제 (잠재 버그 예방)
*   [ ] **Frontend Composables**: 비즈니스 로직 분리 (Pinia 다이어트)    
---

## 📄 라이선스 (License)

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 
