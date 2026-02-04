# API Layer

## 개요

RESTful API 엔드포인트를 정의하는 계층입니다. FastAPI의 라우터 패턴을 사용하여 각 도메인별로 엔드포인트를 분리했습니다.

## 디렉토리 구조

```
api/
├── routers.py          # 메인 라우터 (모든 v1 라우터 통합)
└── v1/
    ├── auth.py         # 인증/인가 (Google OAuth, JWT)
    ├── generator.py    # 테스트 코드 생성 (핵심 기능)
    ├── health.py       # 헬스체크
    └── deps.py         # 의존성 주입 (DI)
```

## 주요 엔드포인트

### 1. **인증 (`/api/auth`)**

| Method | Path | 설명 | 인증 필요 |
|--------|------|------|----------|
| POST | `/auth/google` | Google OAuth 로그인 | ❌ |
| POST | `/auth/verify` | JWT 토큰 검증 | ✅ |

### 2. **테스트 생성 (`/api/generate`)**

| Method | Path | 설명 | 인증 필요 |
|--------|------|------|----------|
| POST | `/generate` | SSE 스트리밍으로 테스트 코드 생성 | ✅ |

**Request Body:**
```json
{
  "input_code": "def add(a, b): return a + b",
  "language": "python",
  "model": "gemini-3-flash-preview",
  "turnstile_token": "xxx",
  "is_regenerate": false
}
```

**Response:** `text/event-stream` (SSE)
```
data: {"type": "chunk", "content": "def test_add():"}
data: {"type": "chunk", "content": "\n    assert add(1, 2) == 3"}
data: {"type": "done"}
```

### 3. **헬스체크 (`/api/health`)**

| Method | Path | 설명 |
|--------|------|------|
| GET | `/health` | 서버 상태 확인 |

## 의존성 주입 (DI)

`deps.py`에서 서비스 인스턴스를 제공합니다:

```python
from src.api.v1.deps import (
    get_test_generator_service,  # TestGeneratorService
    limiter                        # Rate Limiter
)

@router.post("/generate")
@limiter.limit("5/minute")
async def generate_test(
    service: TestGeneratorService = Depends(get_test_generator_service)
):
    ...
```

## Rate Limiting

**설정:** 5 requests/minute (사용자별)

```python
@limiter.limit("5/minute")
async def generate_test(request: Request, ...):
    # request.state.user 기반으로 제한
```

## 보안

- **JWT 인증:** `get_current_user` dependency
- **Turnstile 검증:** 각 요청마다 verify
- **CORS:** `settings.allowed_origins_list`
- **Rate Limiting:** slowapi

## 에러 응답

```python
# ValidationError는 200 OK로 반환 (콘솔 깔끔하게 유지)
{
  "type": "error",
  "status": "validation_error",
  "detail": {
    "code": "EMPTY_CODE",
    "message": "코드를 입력해주세요"
  }
}

# 일반 에러는 적절한 HTTP 상태 코드 사용
{
  "detail": "Unauthorized"
}
```

## 확장 방법

새 엔드포인트 추가 시:

1. `v1/` 아래 새 파일 생성 (예: `v1/history.py`)
2. 라우터 정의
3. `routers.py`에 등록

```python
# routers.py
from src.api.v1 import auth, generator, health, history

api_router.include_router(history.router, prefix="/history", tags=["history"])
```
