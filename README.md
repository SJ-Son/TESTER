# LLM 기반 단위 테스트 자동 생성 시스템: TESTER

[![Deployment](https://img.shields.io/badge/Deploy-Google%20Cloud%20Run-blue?logo=google-cloud)](https://github.com/SJ-Son/TESTER) 
[![Tech Stack](https://img.shields.io/badge/Stack-Full--Stack%20AI-green)](https://github.com/SJ-Son/TESTER)

## 1. 프로젝트 개요
사용자가 입력한 소스 코드를 분석하여 Unit Test 코드를 자동 생성하는 시스템입니다. LLM의 코드 이해 능력을 활용하되, 생성 오류를 최소화하기 위한 검증 로직과 안정적인 서비스 운영을 위한 보안 및 배포 자동화 구현에 중점을 두었습니다.

---

## 2. 주요 구현 사항

### 성능 최적화 및 코드 품질
- **미들웨어 최적화**: API 요청 시 발생하는 중복 모듈 로드(JWT 등)를 전역 스코프로 이동하여 응답 지연을 최소화했습니다.
- **모델 인스턴스 캐싱**: 동일 설정의 GenerativeModel 인스턴스를 재사용(@lru_cache)하여 메모리 효율과 초기 응답 속도를 개선했습니다.
- **코드 중복 제거(DRY)**: 언어별(Python, Java, JS) 유효성 검사 로직을 베이스 클래스로 통합하여 유지보수성을 확보했습니다.

### LLM 제어 및 유효성 검사
- **언어 적합성 판별**: 입력 코드와 선택 언어의 일치 여부를 정규표현식으로 사전 검증하여 불필요한 API 호출을 차단합니다.
- **시스템 지시문 최적화**: AI에게 QA 엔지니어 역할을 부여하고 순수 코드 문자열만 출력하도록 페르소나를 정밀 제어했습니다.

### 보안 및 운영 안정성
- **사용자 인증**: Google OAuth 2.0 및 JWT 기반의 인증 체계를 구축하여 인가된 사용자만 접근 가능하도록 제한했습니다.
- **부정 사용 방지**: reCAPTCHA v3를 통한 봇 차단 및 Rate Limit(호출 횟수 제한)을 적용하여 서버 부하를 관리합니다.

### CI/CD 파이프라인
- **환경 분리(Staging/Production)**: 개발 및 운영 환경을 분리하여 신규 기능의 안정성을 검증한 후 배포합니다.
- **배포 효율화**: 변경된 파일 경로를 감지하여 불필요한 빌드를 방지하는 트리거 조건을 설정했습니다.
- **컨테이너화**: Docker를 사용하여 실행 환경을 표준화하고 Google Cloud Run에 자동 배포합니다.

---

## 3. 기술 스택 (Tech Stack)

| 구분 | 기술 | 도입 이유 |
| --- | --- | --- |
| **Backend** | FastApi (Python) | 비동기 기반의 실시간 스트리밍 응답 처리에 최적화 |
| **Frontend** | Vue 3, Tailwind CSS | 컴포넌트 기반의 빠른 UI 개발 및 매끄러운 사용자 경험 제공 |
| **AI API** | Google Gemini | 높은 코드 이해도와 빠른 추론 성능 활용 |
| **Infrastructure** | Cloud Run, Docker | 서버리스 환경을 통한 유연한 확장성 및 관리 편의성 |

---

## 3. 프로젝트 구조

```text
├── backend/            # FastAPI 기반 API 서버
│   ├── src/            # 핵심 비즈니스 로직 및 보안 설정
│   └── tests/          # 단위, 통합, 보안, 카오스 테스트 스크립트
├── frontend/           # Vue 3 SPA 프론트엔드
├── .github/workflows/  # CI/CD 자동화 설정
└── Dockerfile          # 애플리케이션 패키징 설정
```

## 5. 실행 및 테스트

### 로컬 실행
```bash
# Backend
cd backend && pip install -r requirements.txt
python src/main.py

# Frontend
cd frontend && npm install && npm run dev
```

### 테스트 실행
```bash
# 전체 테스트 suite 실행 (21 items)
export PYTHONPATH=.
python3 -m pytest backend/tests/
```
