# Utility Module Guide

백엔드 공통 유틸리티 모듈 사용법 정리.

## 1. Security (`src.utils.security`)

### 역할
- **AES 암호화**: 민감 데이터(소스코드, 토큰 등)를 암호화하여 DB에 저장.
- **Fail-Closed**: 키가 없거나 암호화 실패 시 절대 평문을 반환하지 않고 에러(Exception)를 발생시킴.

### 사용법

```python
from src.utils.security import EncryptionService

service = EncryptionService()

# 암호화 (평문 -> Base64 Encrypted String)
encrypted_token: str = service.encrypt("sensitive_data")

# 복호화 (Base64 Encrypted String -> 평문)
plain_text: str = service.decrypt(encrypted_token)
```

### 주의사항
- `DATA_ENCRYPTION_KEY` 환경 변수 필수 (32 byte key -> Base64 encoded).
- DB에 저장되는 모든 코드는 반드시 암호화되어야 함.

---

## 2. Logger (`src.utils.logger`)

### 역할
- **구조화된 로깅**: JSON 포맷, Context 정보(User ID, Request ID 등) 포함 가능.
- **표준화**: `logging.getLogger`를 래핑하여 일관된 로그 포맷 제공.

### 사용법

```python
from src.utils.logger import get_logger

logger = get_logger(__name__)

# 일반 로그
logger.info("서버 시작")

# 컨텍스트 로그 (권장)
# user_id, request_id 등 추적 필요한 정보를 함께 남길 때 사용
logger.info_ctx(
    "사용자 로그인 성공", 
    user_id="user_123", 
    ip="127.0.0.1"
)

# 에러 로그
try:
    ...
except Exception as e:
    logger.error_ctx("DB 연결 실패", error=str(e), retry_count=3)
```

### 로그 레벨 정책
- `DEBUG`: 개발 중 디버깅 정보 (프로덕션에서는 비활성화 권장)
- `INFO`: 정상적인 흐름, 주요 이벤트 (로그인, 생성 완료)
- `WARNING`: 예외적이지만 서비스 지속 가능한 상황 (Redis 연결 실패 등)
- `ERROR`: 요청 실패, 예외 발생
- `CRITICAL`: 서비스 불가, 즉시 조치 필요 (필수 환경 변수 누락 등)
