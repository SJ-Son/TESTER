# TestCased: 단위 테스트 자동 생성기

**Live Demo**: [https://testcased.dev](https://testcased.dev)

## 1. 프로젝트 소개
작성한 코드를 붙여넣으면 AI(Google Gemini)가 분석하여 적절한 단위 테스트(Unit Test) 코드를 만들어주는 웹 서비스입니다.
테스트 코드 작성이 번거로워 테스트를 소홀히 하게 되는 문제를 해결하기 위해 만들었습니다.

**개발 기간**: 2026.01 ~ 2026.02 (1인 개발)

---

## 2. 주요 기능 및 기술적 특징

### 2.1. 서울 리전 도메인 연결 (Firebase Proxy)
Cloud Run 서울 리전(asia-northeast3)은 커스텀 도메인 매핑을 직접 지원하지 않습니다.
이를 해결하기 위해 **Firebase Hosting을 앞단에 두고, `rewrites` 설정을 통해 Cloud Run으로 요청을 프록시**하도록 구성했습니다.
결과적으로 서울 리전의 낮은 응답 속도(Latency)와 전용 도메인(`testcased.dev`)을 동시에 확보했습니다.

### 2.2. 실시간 응답 처리 (SSE Streaming)
AI가 코드를 생성하는 데 시간이 걸리기 때문에, 사용자가 마냥 기다리지 않도록 **Server-Sent Events(SSE)**를 도입했습니다.
백엔드에서 생성되는 텍스트 청크(Chunk)를 프론트엔드로 실시간 전송하여, 타이핑하는 듯한 UI를 구현했습니다.

### 2.3. 보안 구성 (IAM & Security)
- **최소 권한 원칙**: 빌드/배포용 계정과 실제 런타임용 서비스 계정을 분리하여, 만약 서버가 탈취되더라도 인프라 전체가 위험해지지 않도록 권한을 제한했습니다.
- **인증**: Google OAuth 2.0을 사용해 검증된 사용자만 서비스를 이용하도록 했습니다.

---

## 3. 기술 스택

| 영역 | 사용 기술 |
| :--- | :--- |
| **Backend** | Python, FastAPI |
| **Frontend** | Vue 3, Pinia, Tailwind CSS |
| **AI** | Google Gemini 2.0 Flash |
| **Infra** | Google Cloud Run, Firebase Hosting |
| **CI/CD** | GitHub Actions, Docker |

---

## 4. 실행 방법

**로컬 개발 환경**
```bash
# Backend 실행
cd backend
pip install -r requirements.txt
python src/main.py

# Frontend 실행
cd frontend
npm install
npm run dev
```
