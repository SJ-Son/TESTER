# API Layer 메모

RESTful API 엔드포인트 정의 계층. FastAPI 라우터 패턴 사용.
도메인별로 `v1/` 아래에 분리해둠.

## 디렉토리 구조
- `routers.py`: 메인 라우터. 여기서 v1 하위 라우터들 다 합침.
- `v1/auth.py`: 인증 관련 (Google OAuth, JWT).
- `v1/generator.py`: 핵심 기능. 테스트 코드 생성.
- `v1/health.py`: 헬스체크. Load Balancer가 씀.
- `v1/deps.py`: 의존성 주입(DI) 모음.

## 주요 엔드포인트

### 1. 인증
- `POST /auth/google`: 구글 로그인. ID Token 받아서 검증하고 우리 JWT 발급해줌.
- `POST /auth/verify`: 발급해준 JWT가 유효한지 체크. (프론트 앱 로딩 때 사용)

### 2. 테스트 생성 (`/generate`)
- `POST /generate`: SSE 스트리밍 방식.
- 특징: `text/event-stream`으로 응답. 한 글자씩 옴.
- Turnstile 토큰 검증 필수.

### 3. 코드 실행 (`/execute`)
- `POST /execute`: 생성된 코드를 실행.
- 내부적으로 Worker VM에 요청을 토스함 (Proxy 역할).

## 구현 디테일

### Rate Limiting
- `slowapi` 사용.
- IP 혹은 User ID 기반으로 5 request/minute 제한. (테스트 땐 좀 풀어줄 필요 있음)

### 의존성 주입 (DI)
- `deps.py` 함수들(`get_test_generator_service`, `get_generation_repository` 등)을 `Depends()`로 주입받음.
- 테스트 할 때 편함.

### 에러 처리
- Pydantic Validation Error는 200 OK로 내려서 프론트가 처리하게 함 (콘솔 에러 방지).
- 그 외 비즈니스 로직 에러는 적절한 4xx, 5xx 사용.
