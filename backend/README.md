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

## v0.7.0 최신 개선사항 ⭐

### 안정성 개선 (P0 - Critical Fixes)
- ✅ **GeminiService Final 변수 보호**: 인스턴스 캐싱으로 Final 변수 재할당 방지
- ✅ **데이터 손실 방지**: 백그라운드 저장 → 동기 저장 전환, 실패 시 사용자 경고
- ✅ **Redis 연결 안정화**: Singleton 패턴 + TCP Keepalive 적용
- ✅ **Graceful Shutdown**: lifespan에서 Redis 연결 정리
- ✅ **History API 타입 정합성**: UUID/datetime 타입 일치로 ResponseValidationError 해결

### 코드 품질 개선 (P1 - Urgent Improvements)
- ✅ **Magic Number 제거**: 모든 상수를 `constants.py`로 중앙화
- ✅ **에러 메시지 한글화**: 95% 한글 메시지 통일 (`ErrorMessages` 클래스)
- ✅ **Health Check 강화**: Redis/Supabase latency, connection pool 정보 제공
- ✅ **성능 최적화**: CacheService에 LRU 캐싱 적용 (SHA256 연산 최적화)
- ✅ **Fail-Fast 원칙**: SupabaseService 초기화 시 ConfigurationError 명시

### 테스트 커버리지 향상
- **전체 커버리지**: 49% → **70%** (+21%p)
- **ExecutionService**: **100%** 커버리지 달성 (15개 신규 테스트)
- **Auth**: 27% → **93%**
- **GeminiService**: 29% → **90%**
- **GenerationRepository**: 44% → **93%**
- **핵심 서비스**: 모두 80%+ 달성

---

## 코드 리팩토링 (v0.7.0+)

### 타입 시스템
- **`types.py`**: 도메인 타입 정의
  - `ValidationResult`, `CacheMetadata`: frozen dataclass
  - `UserId`, `CacheKey`: NewType 기반 타입
  - `LanguageCode`, `ModelName`: Literal 타입
  
- **`config/constants.py`**: 상수 관리
  - `ErrorMessages`: 한글 에러 메시지 45개
  - `NetworkConstants`: HTTP timeout, 압축, 연결 풀 설정
  - `SecurityConstants`, `CacheConstants`: 보안/캐싱 파라미터
  - `Final` 타입 어노테이션으로 불변성 보장
  
- **`exceptions.py`**: 예외 처리
  - 계층적 예외 구조 (TesterException 기반)
  - 컨텍스트 정보 포함 (timestamp, code, context)
  - 도메인별 예외 클래스 (ValidationError, SecurityError, CacheError 등)

### 코드 패턴
- Frozen dataclass 사용
- 튜플 대신 명명된 타입 반환
- 예외 명시적 전파 (silent fail 금지)
- Guard clauses 적용
- Singleton 패턴 (Redis, Supabase 연결 관리)

### 문서화
- Google-style docstring
- 한글 주석
- 타입 힌트 100%

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

### 4. Startup Validation (v0.5.2+, Enhanced v0.7.0)
- **목적**: 필수 환경 변수 누락 시 조기 발견.
- **구현**: `main.py`의 `lifespan`에서 검증:
  - 필수 secrets: `GEMINI_API_KEY`, `DATA_ENCRYPTION_KEY`
  - Supabase 연결: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`
  - Redis 연결: ping 테스트, 실패 시 경고 (degraded mode)
- **효과**: 서버 시작 시점에 설정 문제를 바로 알려줌. 운영 중 에러 방지.

### 5. 인증 시스템 (Supabase Auth)
- **변경**: 자체 JWT 발급 → Supabase 토큰 검증 방식으로 전환.
- **장점**: 세션 관리를 Supabase에 위임, 백엔드는 Stateless로 유지.
- **구현**: `auth.py`에서 Supabase JWT를 `SUPABASE_JWT_SECRET`으로 검증.

### 6. Enhanced Health Check (v0.7.0)
- **엔드포인트**: `/health`
- **제공 정보**:
  - Redis: 연결 상태, latency (ms), connection pool 정보
  - Supabase: 연결 상태, latency (ms), 테이블 접근 가능 여부
  - Gemini API: 설정 상태, 사용 모델 정보
  - 서버: 버전, 타임스탬프
- **용도**: Load balancer health check, 서비스 모니터링

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
python3 -m venv .venv
source .venv/bin/activate

# 패키지 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일 편집

# 실행 (Reload 모드)
uvicorn src.main:app --reload
```

## 테스트

```bash
# 전체 테스트 실행
pytest tests/ -v

# 커버리지 포함
pytest tests/ --cov=src --cov-report=term-missing

# 특정 모듈만
pytest tests/unit/test_execution_service.py -v

# 커버리지 리포트 생성
pytest --cov=src --cov-report=html
# htmlcov/index.html 에서 확인
```

**현재 테스트 커버리지**: 70% (상위 서비스 80%+)
