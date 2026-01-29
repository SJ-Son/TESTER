# LLM 기반 단위 테스트 자동 생성 시스템: TESTER

## 1. 프로젝트 개요
소스 코드를 분석하여 실행 가능한 단위 테스트 코드를 자동 생성하는 도구입니다. 단순한 코드 생성을 넘어, LLM의 환각 현상을 제어하고 시스템 강건성을 검증하는 **엔지니어링 신뢰성** 확보에 초점을 맞췄습니다.

## 2. 핵심 경쟁 우위 (USP)

### 왜 Gemini Advanced 대신 TESTER인가?
- **신뢰의 자동화 (2-Pass Reflection):** 생성된 코드를 즉시 실행하고 문법/논리적 오류를 스스로 보정하는 피드백 루프를 통해 "바로 실행 가능한" 코드를 보장합니다.
- **강건성 검증 (Chaos Testing):** 단순한 성공 케이스(Happy Path)를 넘어, 비정상 입력 및 프롬프트 주입 공격 등에 대한 방어력을 실시간으로 검증합니다.
- **표준화된 품질:** 전략 패턴(Strategy Pattern)을 통해 개발자별 편차 없이 프로젝트 표준에 부합하는 테스트 코드를 생성합니다.

## 3. 기술 스택
- **Frontend:** Vue.js 3, Vite, Tailwind CSS v4
- **Backend:** Python 3.12, FastAPI (Async SSE Streaming)
- **Infrastructure:** Docker (Multi-stage build), GitHub Actions, Google Cloud Run (Staging/Prod)

## 4. 고도화된 CI/CD 파이프라인
운영 안정성을 위해 다단계 배포 프로세스를 채택하고 있습니다.

1. **Staging (사전 검증):** `develop` 브랜치에 Push 시 `tester-staging` 서비스로 자동 배포됩니다.
2. **Production (상용 배포):** Git Release Tag (`v*`) 생성 시 `tester-prod` 서비스로 배포됩니다. (수동 승인 효과)

## 5. 프로젝트 구조
```text
├── backend/            # API 서버 및 LLM Reflection 로직
├── frontend/           # Vue.js 기반 인터랙티브 UI
├── tests/              # 고립/강건성(Chaos) 테스트 스크립트
├── .github/workflows/  # Staging/Prod 분리된 배포 파이프라인
└── Dockerfile          # 컨테이너화 설정
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
