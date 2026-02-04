# Service Layer

## 개요

비즈니스 로직을 담당하는 계층입니다. API 레이어와 데이터 레이어 사이에서 핵심 로직을 처리합니다.

## 서비스 목록

### 1. **TestGeneratorService**
**역할:** 테스트 코드 생성의 오케스트레이션

```python
class TestGeneratorService:
    def __init__(self, gemini_service: GeminiService):
        self.gemini_service = gemini_service
    
    async def generate_test(self, code, language, model):
        # 1. 언어 전략 선택
        strategy = LanguageFactory.get_strategy(language)
        
        # 2. 코드 검증
        is_valid, error_msg = strategy.validate_code(code)
        if not is_valid:
            raise ValidationError(error_msg)
        
        # 3. 시스템 프롬프트 생성
        system_instruction = strategy.get_system_instruction()
        
        # 4. AI 생성 호출
        async for chunk in self.gemini_service.generate_test_code(...):
            yield chunk
```

**책임:**
- Language Strategy 선택 및 검증
- Prompt 컨텍스트 생성
- GeminiService 호출

---

### 2. **GeminiService**
**역할:** Google Gemini API 호출 및 캐싱

```python
class GeminiService:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.DEFAULT_GEMINI_MODEL
        self.cache = CacheService()
    
    async def generate_test_code(
        self,
        source_code: str,
        system_instruction: str,
        stream: bool = True,
        is_regenerate: bool = False
    ):
        # 1. 캐시 키 생성
        cache_key, ttl = self.cache.generate_key(...)
        
        # 2. 캐시 확인 (재생성 아닐 경우)
        if not is_regenerate:
            cached = self.cache.get(cache_key)
            if cached:
                yield cached
                return
        
        # 3. API 호출
        temperature = 0.7 if is_regenerate else 0.2
        response = await model.generate_content_async(...)
        
        # 4. 스트리밍 & 캐시 저장
        async for chunk in response:
            yield chunk.text
        self.cache.set(cache_key, full_response, ttl=ttl)
```

**특징:**
- **재시도 로직:** `@retry` (최대 3회, exponential backoff)
- **캐싱:** Redis 활용 (2시간 TTL)
- **Temperature 제어:** 재생성 시 0.7 (창의적), 일반 시 0.2 (안정적)

---

### 3. **CacheService**
**역할:** Redis 기반 캐싱

```python
class CacheService:
    def __init__(self, redis_url: str = settings.REDIS_URL):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
    
    def generate_key(self, *args, strategy: CacheStrategy):
        # SHA256 해시 기반 키 생성
        # 반환: (cache_key, ttl_seconds)
        return key, strategy.ttl
```

**캐싱 전략:**

| 전략 | TTL | 용도 |
|------|-----|------|
| `GEMINI_RESPONSE` | 2시간 | 동일 코드 재요청 시 즉시 응답 |
| `USER_HISTORY` | 30분 | 세션 기반 임시 저장 |
| `VALIDATION_RULE` | 24시간 | 언어별 검증 규칙 (자주 변경 안 됨) |

---

### 4. **SupabaseService**
**역할:** PostgreSQL 데이터베이스 통신

```python
class SupabaseService:
    def save_generation_history(self, user_id, code, result, language):
        # generation_history 테이블에 저장
        # 암호화된 컬럼: code, result (Fernet)
```

**특징:**
- Fernet 암호화로 민감 정보 보호
- 비동기 저장 (non-blocking)

---

## 의존성 그래프

```
API Layer
    ↓
TestGeneratorService
    ↓
    ├─→ LanguageFactory (languages/)
    └─→ GeminiService
            ↓
            ├─→ CacheService (Redis)
            └─→ SupabaseService (PostgreSQL)
```

## 테스트 작성 예시

```python
# tests/services/test_gemini_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_generate_with_cache_hit(mocker):
    # Given
    mock_cache = MagicMock()
    mock_cache.get.return_value = "# Cached test code"
    
    service = GeminiService()
    service.cache = mock_cache
    
    # When
    result = []
    async for chunk in service.generate_test_code("def add(): pass", ...):
        result.append(chunk)
    
    # Then
    assert "".join(result) == "# Cached test code"
    mock_cache.get.assert_called_once()
```

## 확장 방법

새 서비스 추가 시:

1. `services/` 아래 새 파일 생성
2. 클래스 정의 (의존성 주입 고려)
3. `deps.py`에 DI 함수 추가

```python
# services/email_service.py
class EmailService:
    def __init__(self, smtp_config: dict):
        self.smtp_config = smtp_config
    
    async def send_welcome_email(self, user_email: str):
        ...

# api/v1/deps.py
def get_email_service() -> EmailService:
    return EmailService(settings.SMTP_CONFIG)
```
