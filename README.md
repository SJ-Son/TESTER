# TESTER

<div align="center">
  
**AI-Powered Test Code Generator**

Gemini API 활용한 테스트 코드 자동 생성 플랫폼.

[![Vue.js](https://img.shields.io/badge/Vue.js-4FC08D?style=for-the-badge&logo=vuedotjs&logoColor=white)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python_3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)

</div>

---

## 📌 프로젝트 개요 및 특징

- **AI 테스트 생성**: Gemini한테 코드 던져주면 Pytest 코드 짜줌.
- **실시간 스트리밍**: SSE(Server-Sent Events) 써서 한 글자씩 타이핑되는 효과 구현.
- **보안**: Supabase Auth 연동, Turnstile, Fernet 암호화 (Fail-Closed 적용).
  > **Note**: `SUPABASE_JWT_SECRET`, `DATA_ENCRYPTION_KEY`, `GEMINI_API_KEY` 환경변수가 없으면 서버가 시작되지 않습니다.
- **캐싱**: Redis 사용. AI 응답은 2시간 캐싱해서 비용 아낌.
- **Hybrid 아키텍처**:
  - 웹/API: Cloud Run (Serverless)
  - 실행: GCE VM (Docker Sandbox) -> 보안 때문에 격리함.
  - **안정성**: `put_archive` 기반의 안전한 코드 주입 & 비동기 실행 보장.

## 📚 모듈별 학습 메모 (Documentation)

각 파트별 상세 구현 내용이나 설계 의도는 아래 메모 참고.

| 모듈 | 설명 | 링크 |
| :--- | :--- | :--- |
| **Backend** | FastAPI 구조, 비동기, 레이어 | [👉 Backend 메모](./backend/README.md) |
| &nbsp;&nbsp; _API_ | API 엔드포인트 설계 | [👉 API 가이드](./backend/src/api/00_API_GUIDE.md) |
| &nbsp;&nbsp; _Services_ | 비즈니스 로직 상세 | [👉 Service 가이드](./backend/src/services/00_SERVICE_GUIDE.md) |
| &nbsp;&nbsp; _Strategies_ | 언어별 전략 패턴 구현 | [👉 Strategy 가이드](./backend/src/languages/00_LANGUAGE_STRATEGY_GUIDE.md) |
| **Frontend** | Vue 3, Pinia, 컴포넌트 설계 | [👉 Frontend 메모](./frontend/00_FRONTEND_GUIDE.md) |
| &nbsp;&nbsp; _Components_ | UI 컴포넌트 역할 | [👉 Component 가이드](./frontend/src/components/00_COMPONENTS_GUIDE.md) |
| **Worker** | Docker 샌드박스 VM 운영 | [👉 Worker 메모](./worker/00_WORKER_GUIDE.md) |
| **History** | 변경 이력 | [👉 CHANGELOG](./CHANGELOG.md) |

## 🏗️ 아키텍처

```mermaid
graph LR
    User([User]) -->|Request| Server[FastAPI Server]
    Server -->|Prompt| LLM[Google Gemini AI]
    LLM -->|Generated Code| Server
    Server -->|Validation| Cache[(Redis Cache)]
    Server -->|Store| Repo[Repository] --> DB[(Supabase)]
    Server -->|Response| User
    Server -.->|Background Task| Repo
    
    note right of Repo: 암호화/저장 보장
    
    subgraph "Hybrid Execution"
    Server -->|HTTP/Auth| Worker[Worker VM]
    Worker -->|Docker| Sandbox[Test Container]
    end
```

## 🛠 기술 스택

- **Backend**: Python 3.12, FastAPI, Gemini, Supabase(Postgres), Redis
- **Frontend**: Vue 3, TypeScript, Pinia, TailwindCSS, Vite
- **Infra**: Cloud Run, GCE, Docker, GitHub Actions

## 📁 프로젝트 구조

```
TESTER/
├── backend/                 # Main API Server
│   ├── src/
│   │   ├── api/             # Endpoints
│   │   ├── services/        # Business Logic
│   │   └── languages/       # Strategies
│   └── README.md            # Backend Study Memo
│
├── frontend/                # Web Client
│   ├── src/
│   │   ├── components/      # UI Components
│   │   ├── stores/          # Pinia State
│   │   └── ...
│   └── 00_FRONTEND_GUIDE.md # Frontend Study Memo
│
├── worker/                  # Execution Worker (GCE)
│   ├── main.py              # Worker API
│   └── 00_WORKER_GUIDE.md   # Worker Study Memo
│
└── .github/workflows/       # CI/CD Pipelines
```

## 🚀 빠른 시작 (Local)

```bash
# 1. 클론
git clone https://github.com/SJ-Son/TESTER.git
cd TESTER

# 2. 백엔드 실행
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn src.main:app --reload

# 3. 프론트엔드 실행
cd frontend
npm install
cp .env.example .env
npm run dev
```

**접속**: http://localhost:5173

## 📄 라이선스

MIT License 

---
