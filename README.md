# LLM 기반 단위 테스트 자동 생성 시스템: TESTER

## 1. 프로젝트 개요
소스 코드를 분석하여 실행 가능한 단위 테스트 코드를 자동 생성하는 도구입니다. LLM 기반 생성 과정에서 발생할 수 있는 환각 현상(Hallucination)과 문법 오류를 제어하기 위한 검증 시스템 구현에 초점을 맞췄습니다.

## 2. 주요 해결 과제 (QA Engineering)

### 정확성 보장을 위한 2단계 검증 (Reflection)
1. **Pass 1 (Draft):** 입력된 소스 코드에 기반한 1차 테스트 코드 생성.
2. **Pass 2 (Refinement):** 생성된 코드를 다시 분석하여 문법 오류, 라이브러리 누락(Import), 언어 혼용 여부를 스스로 검토하고 보정하는 피드백 루프를 구현했습니다.

### 유연한 확장을 위한 전략 패턴 (Strategy Pattern)
- 언어별로 상이한 문법 검증 로직과 프롬프트를 모듈화했습니다.
- 인터페이스화를 통해 Python, Java, JavaScript 외 추가 언어 지원 시 기존 코드의 수정 없이 확장이 가능하도록 설계했습니다.

### 시스템 안정성 검증 (Chaos Testing)
- 비정상 입력(혼종 코드, 파편화된 코드, 프롬프트 주입 공격 등)에 대한 시스템의 예외 처리 및 회복 탄력성을 확인하는 자동화 테스트 스위트를 구축했습니다.

## 3. 기술 스택
- **Frontend:** Vue.js 3, Vite, Tailwind CSS v4
- **Backend:** Python 3.12, FastAPI (Async SSE Streaming)
- **Infrastructure:** Docker (Multi-stage build), GitHub Actions (CI/CD), Cloud Run

## 4. CI/CD 파이프라인
GitHub `main` 브랜치 Push 시 다음 과정이 자동 수행됩니다.
1. Docker Buildx를 활용한 멀티 스테이지 빌드 및 레이어 캐싱.
2. Google Artifact Registry 이미지 업로드.
3. Google Cloud Run 최신 리비전 배포.

## 5. 프로젝트 구조
```text
├── backend/            # API 서버 및 LLM Reflection 로직
├── frontend/           # Vue.js 기반 인터랙티브 UI
├── tests/              # 고립/강건성(Chaos) 테스트 스크립트
└── Dockerfile          # 컨테이너화/배포 설정
```

## 6. 실행 방법
```bash
# Backend
cd backend && pip install -r requirements.txt
python src/main.py

# Frontend
cd frontend && npm install && npm run dev

# Tests
python tests/chaos_runner.py
```
