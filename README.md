# TestCased: AI 기반 단위 테스트 자동 생성 시스템

[![Live Demo](https://img.shields.io/badge/Live%20Demo-testcased.dev-blue?style=for-the-badge&logo=google-chrome)](https://testcased.dev)
[![Deployment](https://img.shields.io/badge/Deploy-Google%20Cloud%20Run-4285F4?style=for-the-badge&logo=google-cloud)](https://github.com/SJ-Son/TESTER)
[![Stack](https://img.shields.io/badge/Stack-FastAPI%20%7C%20Vue3-009688?style=for-the-badge)](https://github.com/SJ-Son/TESTER)

> **Live Demo**: [https://testcased.dev](https://testcased.dev)

## 1. 프로젝트 개요
**TestCased**는 개발자가 작성한 소스 코드를 AI가 분석하여 **실무 수준의 Unit Test 코드를 자동으로 생성해 주는 엔지니어링 도구**입니다.
단순한 코드 생성을 넘어, **복잡한 인프라 제약(서울 리전 도메인 매핑)**과 **엔터프라이즈급 보안(IAM Least Privilege)** 요구사항을 해결한 모던 웹 애플리케이션입니다.

---

## 2. 핵심 아키텍처 및 구현 (Highlights)

### 🌐 Hybrid Proxy Architecture (Infra)
- **문제**: Google Cloud Run 서울 리전(asia-northeast3)은 커스텀 도메인 매핑을 직접 지원하지 않음.
- **해결**: **Firebase Hosting을 리버스 프록시(Reverse Proxy)**로 앞단에 배치하여, 서울 리전 서버의 낮은 지연시간(Low Latency)을 유지하면서도 전용 도메인(`testcased.dev`)과 무료 SSL 인증서를 통합 적용.

### 🛡️ DevSecOps & Security
- **최소 권한 원칙(Least Privilege)**: 배포용(`deployer`)과 런타임용(`runtime-sa`) 서비스 계정을 엄격히 분리하여, 서버 탈취 시에도 피해 범위를 최소화하는 보안 아키텍처 구현.
- **인증/인가**: Google OAuth 2.0 및 JWT 기반의 Stateless 인증 시스템 구축.
- **봇 방지**: reCAPTCHA v3 및 IP/User 기반 Rate Limiting을 적용하여 API 남용 방지.

### ⚡ Performance & UX
- **SSE Streaming**: AI의 추론 과정을 실시간 스트리밍(Server-Sent Events)으로 시각화하여 사용자 대기 경험 개선.
- **Contextual UI**: 언어 선택 도구를 에디터 상단에 배치하는 등 개발자 작업 흐름(Workflow)에 최적화된 UX 설계.

### 🚀 CI/CD Automation
- **Git Flow 기반 배포**: `develop` 브랜치 푸시 시 Staging 서버로, `main` 병합 시 Production 서버로 자동 배포되는 파이프라인(GitHub Actions) 구축.

---

## 3. 기술 스택 (Tech Stack)

| 구분 | 기술 | 선정 이유 |
| :--- | :--- | :--- |
| **Backend** | **FastAPI** (Python) | 비동기 지원 및 SSE 스트리밍 구현에 최적화 |
| **Frontend** | **Vue 3**, Pinia, Tailwind | Composition API를 활용한 모듈화 및 빠른 렌더링 성능 |
| **AI Model** | Google **Gemini 2.0** | 대량의 코드 컨텍스트 이해 및 빠른 추론 속도 |
| **Infra** | **Cloud Run** + **Firebase** | 서버리스(Serverless)의 확장성과 엣지 캐싱/라우팅의 결합 |
| **DevOps** | Docker, Artifact Registry, GA | 컨테이너 기반의 표준화된 빌드 및 배포 환경 |

---

## 3. 프로젝트 구조

```text
TESTER/
├── 📂 .github/workflows/      # 분리된 배포 환경 (Prod/Staging)
├── 📂 backend/                # FastAPI 서버 및 AI 로직
│   ├── src/auth.py            # OAuth 및 JWT 보안 모듈
│   └── src/services/          # Gemini AI 연동 및 프롬프트 관리
├── 📂 frontend/               # Vue.js 클라이언트
│   ├── src/stores/            # Pinia 상태 관리 (스트리밍 데이터 처리)
│   └── src/components/        # 재사용 가능한 UI 컴포넌트
├── firebase.json              # 리버스 프록시 라우팅 설정
└── Dockerfile                 # 멀티 스테이지 빌드 설정
```

## 5. 실행 방법

### 로컬 개발 (Local Development)
```bash
# 1. Backend 실행
cd backend
pip install -r requirements.txt
python src/main.py

# 2. Frontend 실행
cd frontend
npm install
npm run dev
```
