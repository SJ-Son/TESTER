# LLM 기반 단위 테스트 자동 생성 시스템 (TESTER)

## 1. 개요 (Overview)
본 프로젝트는 개발 생산성 향상과 코드 품질 보증을 위한 다국어 단위 테스트 자동 생성 시스템입니다. LLM(Gemini 2.0/3.0)의 강력한 추론 능력을 활용하되, 생성된 데이터의 신뢰성을 확보하기 위해 **자가 수정(Self-Correction) 아키텍처**와 **엄격한 구문 검증(Syntax Validation)** 레이어를 결합한 엔지니어링 솔루션입니다.

단순한 코드 생성을 넘어, 생성된 결과물의 실행 가능성을 보장하고 언어별 문법적 특성을 유지하는 데 초점을 맞춘 QA 엔지니어링 관점의 결과물입니다.

## 2. 기술 스택 (Tech Stack)
- **Frontend:** Vue.js 3, Vite, Tailwind CSS v4, Lucide Icons, Highlight.js
- **Backend:** Python 3.12, FastAPI (Asynchronous SSE Streaming), Pydantic (Data Validation)
- **AI/LLM:** Google Gemini API (Flash/Pro 모델군)
- **Testing & Verification:** Pytest, Custom Chaos Testing Suite
- **Infrastructure:** Docker (Multi-stage build), Google Cloud Run (CI/CD 연동)

## 3. 시스템 아키텍처 (Architecture)
본 시스템은 언어별 확장성과 생성 로직의 독립성을 보장하기 위해 모듈화된 아키텍처로 설계되었습니다.

### 전략 패턴 (Strategy Pattern) 적용
Python, Java, JavaScript 등 다양한 프로그래밍 언어를 유연하게 지원하기 위해 `LanguageStrategy` 인터페이스를 구현했습니다.
- **언어별 독립성:** 각 언어 전략 객체는 고유의 문법 검증 로직, 시스템 인스트럭션, 에러 보정 프롬프트를 캡슐화합니다.
- **동적 해결:** `LanguageFactory`를 통해 런타임에 사용자 요청에 맞는 전략 객체를 주입받아 처리합니다.

### 2-Pass Reflection (자가 수정) 데이터 흐름
1. **요청 수신:** Vue.js 클라이언트로부터 소스 코드 및 설정값을 FastAPI로 전달.
2. **사전 검증:** 선택된 `LanguageStrategy`를 통해 입력 코드의 기본 유효성 검사 수행.
3. **초안 생성 (Pass 1):** `GeminiService`를 통해 1차 단위 테스트 코드 생성.
4. **자가 성찰 (Pass 2):** 생성된 초안을 "Strict Syntax Reviewer" 페르소나를 가진 LLM에 재투입하여 Import 누락, 언어 혼용, 문법 오류를 검토하고 필요시 수정.
5. **실시간 스트리밍:** 최종 정제된 코드를 SSE(Server-Sent Events)를 통해 클라이언트에 실시간으로 전달.

## 4. 핵심 기능 및 구현 상세 (Key Features)
- **다국어 문법 가드레일:** Java 코드 결과물에 Python 문법이 섞이는 등의 '언어 오염'을 방지하기 위한 정규식 기반 검증 로직 탑재.
- **비동기 스트리밍 처리:** Python의 `asyncio`와 FastAPI의 `StreamingResponse`를 활용하여 대규모 코드 생성 시에도 끊김 없는 사용자 경험 제공.
- **구문 성찰 피드백 루프:** 생성된 코드가 해당 언어의 표준 라이브러리와 컨벤션을 준수하는지 AI가 스스로 재검토하는 로직 구현.

## 5. 안정성 및 QA 검증 (Robustness & Verification)
### 카오스 테스트 스위트 (Chaos Testing Suite)
시스템의 회복 탄력성(Resilience)과 가드레일 작동 여부를 검증하기 위해 비정상 입력을 주입하는 자동화 스크립트(`tests/chaos_runner.py`)를 구축했습니다.
- **The Chimera Case:** 다국어 혼종 코드를 주입하여 언어 특정 및 거절 로직 검증.
- **The Fragment Case:** 문맥 없는 파편화된 코드를 주입하여 추론 및 보정 능력 확인.
- **The Trap Case:** 실행 코드가 없는 주석 덩어리를 주입하여 환각(Hallucination) 억제력 검증.
- **The Injection Case:** 시스템 프롬프트를 우회하려는 탈옥(Prompt Injection) 시도에 대한 방어력 검증.

### 자동화 평가 도구
`backend/tests/` 내의 `auto_evaluator.py` 등을 통해 CI/CD 파이프라인에서 생성 성공률을 정량적으로 측정할 수 있는 환경을 마련했습니다.

## 6. 프로젝트 구조 (Project Structure)
```text
.
├── backend/                # FastAPI 백엔드 서비스
│   ├── src/
│   │   ├── languages/      # 전략 패턴 기반 언어별 로직
│   │   ├── services/       # 코어 LLM 연동 및 Reflection 로직
│   │   └── main.py         # API 엔트리 포인트
│   └── tests/              # 단위 및 통합 테스트 코드
├── frontend/               # Vue.js 3 SPA 프론트엔드
│   ├── src/
│   │   ├── App.vue         # 메인 인터랙티브 UI
│   │   └── style.css       # Tailwind v4 스타일 정의
│   └── vite.config.ts      # 빌드 설정
├── tests/                  # 시스템 통합 카오스 테스트
├── Dockerfile              # 멀티스테이지 컨테이너 정의
└── README.md               # 기술 문서 (본 파일)
```

## 7. 설치 및 실행 가이드 (Setup & Execution)
### 사전 요구사항
- Python 3.12 이상, Node.js 20 이상
- Google Gemini API Key

### 로컬 백엔드 실행
```bash
cd backend
pip install -r requirements.txt
export GEMINI_API_KEY=your_key_here
python src/main.py
```

### 로컬 프론트엔드 실행
```bash
cd frontend
npm install
npm run dev
```

### 카오스 테스트 수행
```bash
python tests/chaos_runner.py
```
