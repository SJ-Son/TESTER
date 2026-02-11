# API Layer 메모

RESTful API 엔드포인트 정의 계층. FastAPI 라우터 패턴 사용.
도메인별로 `v1/` 아래에 분리해둠.

## 디렉토리 구조
- `routers.py`: 메인 라우터. 여기서 v1 하위 라우터들 다 합침.
- `v1/generator.py`: 핵심 기능. 테스트 코드 생성 (SSE 스트리밍).
- `v1/execution.py`: 코드 실행 요청 (Worker로 프록시).
- `v1/history.py`: 이력 조회/저장 관련 엔드포인트.
- `v1/health.py`: 상세 헬스체크. Redis/Supabase 연결 상태 및 Latency 반환.
- `v1/deps.py`: 의존성 주입(DI) 모음.

## 주요 엔드포인트

### 1. 인증 (Supabase)
- **방식**: 프론트엔드에서 Supabase `signInWithOAuth`로 로그인.
- **토큰 검증**: `Authorization: Bearer <token>` 헤더로 전달된 Supabase JWT를 검증.
- **구현**: `auth.py`의 `get_current_user` dependency에서 처리.
- **주의**: 백엔드는 자체 JWT를 발급하지 않음. Supabase 토큰만 검증.

### 2. 테스트 생성 (`/generate`)
- `POST /api/v1/generate`: SSE 스트리밍 방식.
- **응답 형식**: `text/event-stream`으로 응답. 한 글자씩 옴.
- **보안**: Turnstile 토큰 검증 필수.
- **캐싱**: 동일 요청은 Redis 캐시에서 가져옴 (AI API 비용 절감).

### 3. 코드 실행 (`/execute`)
- `POST /api/v1/execute`: 생성된 코드를 실행.
- **프록시 역할**: 내부적으로 Worker VM에 요청을 토스함.
- **보안**: Worker 통신 시 `WORKER_AUTH_TOKEN` 사용.

### 4. 히스토리 (`/history`)
- `GET /api/v1/history/`: 사용자별 생성 이력 조회 (최근 50개).
- **보안**: 로그인 사용자만 자신의 이력만 볼 수 있음.
- **암호화**: DB에 저장된 코드는 암호화되어 있으며, 조회 시 자동 복호화.

## 구현 디테일

### 5. 사용자 상태 (`/user/status`)
- `GET /api/v1/user/status`: 사용자의 주간 사용량 및 남은 횟수 조회.
- **Quota**: 주간 30회 제한 확인 용도.

## 구현 디테일

### Rate Limiting & User Quota
- `slowapi` 사용 (Redis Backend).
- **Rate Limit**: 5 requests/minute (분당 5회).
- **Weekly Quota**: 30 requests/week (주간 30회).
- 로그인 사용자는 User ID, 비로그인은 IP 기준.


### 의존성 주입 (DI)
- `deps.py` 함수들(`get_test_generator_service`, `get_generation_repository` 등)을 `Depends()`로 주입받음.
- 테스트 할 때 편함. `app.dependency_overrides`로 Mock 주입 가능.

### 에러 처리
- Pydantic Validation Error는 200 OK로 내려서 프론트가 처리하게 함 (콘솔 에러 방지).
- 그 외 비즈니스 로직 에러는 적절한 4xx, 5xx 사용.
- Turnstile 검증 실패 → 400 에러 (`TurnstileError`).

### Background Tasks
- 이력 저장은 `BackgroundTasks`로 처리.
- 클라이언트 연결이 끊겨도 저장 작업은 완료됨.
