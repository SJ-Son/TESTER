# TestCased: 단위 테스트 자동 생성 서비스

[![Live Demo](https://img.shields.io/badge/Live%20Demo-testcased.dev-blue?style=flat-square&logo=google-chrome)](https://testcased.dev)
[![Deployment](https://img.shields.io/badge/Deploy-Google%20Cloud%20Run-4285F4?style=flat-square&logo=google-cloud)](https://github.com/SJ-Son/TESTER)

사용자가 입력한 소스 코드를 분석하여 테스트 코드를 생성해 주는 웹 서비스입니다.
개발 과정에서 번거로운 테스트 코드 작성을 자동화하고, 놓칠 수 있는 예외 케이스를 보완하기 위해 개발했습니다.

## 1. 주요 기술적 특징

### 인프라: Cloud Run & Firebase 구성
- **문제와 해결**: Google Cloud Run 서울 리전(asia-northeast3)이 커스텀 도메인 매핑을 지원하지 않는 문제가 있었습니다. 이를 해결하기 위해 Firebase Hosting을 앞단에 두고, `rewrites` 설정을 통해 Cloud Run으로 트래픽을 전달하는 리버스 프록시 구조를 구축했습니다.
- **결과**: 서울 리전의 빠른 응답 속도를 유지하며 커스텀 도메인과 SSL 인증서를 적용했습니다.

### 보안: IAM 권한 분리
- **서비스 계정 분리**: CI/CD 배포를 담당하는 계정과 실제 서버를 실행하는 계정(`runtime-sa`)을 분리했습니다.
- **최소 권한 원칙**: 런타임 계정에는 로그 적재 등 실행에 필수적인 권한만 부여하여 보안 위험을 줄였습니다.

### 개발 환경: CI/CD 자동화
- **배포 파이프라인**: GitHub Actions를 사용하여 `develop` 브랜치는 스테이징 서버로, `main` 브랜치는 운영 서버로 배포되도록 자동화했습니다.
- **Docker**: 환경 일관성을 위해 전체 애플리케이션을 도커 컨테이너로 패키징하여 배포합니다.

## 2. 사용 기술

| 구분 | 기술 스택 |
| :--- | :--- |
| **Frontend** | Vue 3, Pinia, Tailwind CSS |
| **Backend** | FastAPI (Python) |
| **AI** | Google Gemini 2.0 Flash |
| **Infra** | Google Cloud Run, Firebase Hosting |
| **DevOps** | Docker, GitHub Actions |

## 3. 프로젝트 구조

```text
TESTER/
├── .github/workflows/      # CI/CD 설정 (Prod/Staging 분리)
├── backend/                # FastAPI 서버
│   ├── src/auth.py         # Google OAuth 인증 처리
│   └── src/main.py         # API 엔트리포인트 및 SSE 스트리밍
├── frontend/               # Vue.js 클라이언트
│   └── src/stores/         # Pinia 상태 관리
├── firebase.json           # 호스팅 및 리버스 프록시 설정
└── Dockerfile              # 배포용 이미지 빌드 설정
```

## 4. 로컬 실행 방법

**Backend**
```bash
cd backend
pip install -r requirements.txt
python src/main.py
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```
