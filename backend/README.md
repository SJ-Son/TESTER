# Backend 학습 메모

TESTER 백엔드 아키텍처 및 핵심 로직 정리.

## 아키텍처 개요

### FastAPI & Async IO
- **선택 이유**: AI 서비스 특성상 I/O Bound 작업(Gemini API 대기, DB 조회 등)이 많음. 동기 방식(Flask/Django)보다 비동기 처리가 효율적이라 판단.
- **특징**: `async def`로 정의된 함수들은 이벤트 루프에서 관리됨. 요청 대기 시간에 다른 작업을 처리할 수 있어 처리량(Throughput)이 높음.

### Directory Structure (Layered)
역할별로 확실하게 분리함.
- `api/`: 컨트롤러 역할. 요청/응답 처리만 담당.
- `services/`: 비즈니스 로직. 실제 일(AI 호출, DB 저장)은 여기서 다 함.
- `repositories/`: 데이터베이스 접근 계층. 암호화/복호화 포함.
- `config/`: 환경 변수 관리 (`pydantic-settings` 사용).

---

## 코드 리팩토링 (v0.7.0+)

### 타입 시스템
- **`types.py`**: 도메인 타입 정의
  - `ValidationResult`, `CacheMetadata`: frozen dataclass
  - `UserId`, `CacheKey`: NewType 기반 타입
  - `LanguageCode`, `ModelName`: Literal 타입
  
- **`config/constants.py`**: 상수 관리
  - `Final` 타입 어노테이션
  - 도메인별 클래스 그룹화
  - 한글 docstring
  
- **`exceptions.py`**: 예외 처리
  - 계층적 예외 구조
  - 컨텍스트 정보 포함
  - 도메인별 예외 클래스

### 코드 패턴
- Frozen dataclass 사용
- 튜플 대신 명명된 타입 반환
- 예외 명시적 전파
- Guard clauses 적용

### 문서화
- Google-style docstring
- 한글 주석

---

## 주요 구현 포인트

### 1. 실시간 스트리밍 (SSE)
- **문제**: LLM 응답이 오래 걸림.
- **해결**: Server-Sent Events 도입.
- **구현**: `src/api/v1/generator.py`에서 `yield`를 사용한 제너레이터 패턴 적용. 한 덩어리(chunk) 만들어질 때마다 바로 클라이언트로 쏴줌.

### 2. 의존성 주입 (Dependency Injection)
- **목적**: 결합도 낮추기 & 테스트 용이성.
- **방법**: `Depends()` 사용.
- **효과**: 테스트 코드 짤 때 `override_dependency`로 Mock 객체를 쉽게 주입할 수 있었음. (DB 없이 테스트 가능)

### 3. Hybrid Architecture (Cloud Run + Worker VM)
- **구조**:
  - Web Server (Cloud Run): 가벼운 API 처리.
  - Worker (GCE VM): 무거운 Docker 실행 담당.
- **이유**: Cloud Run에서는 Docker-in-Docker 실행이 까다롭고 보안상 좋지 않음. 실행 환경을 아예 물리적으로 격리해버림.
- **통신**: `ExecutionService`가 `httpx`로 Worker API 호출. (`WORKER_AUTH_TOKEN`으로 인증)

### 4. Startup Validation (v0.5.2+)
- **목적**: 필수 환경 변수 누락 시 조기 발견.
- **구현**: `main.py`의 `lifespan`에서 `DATA_ENCRYPTION_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` 체크.
- **효과**: 서버 시작 시점에 설정 문제를 바로 알려줌. 운영 중 에러 방지.

### 5. 인증 시스템 (Supabase Auth)
- **변경**: 자체 JWT 발급 → Supabase 토큰 검증 방식으로 전환.
- **장점**: 세션 관리를 Supabase에 위임, 백엔드는 Stateless로 유지.
- **구현**: `auth.py`에서 Supabase JWT를 `SUPABASE_JWT_SECRET`으로 검증.

---

## 필수 환경 변수

서버 실행에 반드시 필요한 환경 변수 목록:

```bash
# AI 서비스
GEMINI_API_KEY=your-gemini-api-key

# 데이터베이스 (Supabase)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret
SUPABASE_ANON_KEY=your-anon-key

# 보안
DATA_ENCRYPTION_KEY=base64-encoded-32-byte-key
TURNSTILE_SECRET_KEY=your-turnstile-secret

# Worker 통신
WORKER_URL=http://worker-vm-ip:5000
WORKER_AUTH_TOKEN=your-worker-token

# Redis (선택)
REDIS_URL=redis://localhost:6379
```

---

## 셋업 메모

```bash
# 가상환경
python3 -m venv venv
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일 편집

# 실행 (Reload 모드)
uvicorn src.main:app --reload
```

테스트 실행:
```bash
pytest tests/ -v --cov=src
```
