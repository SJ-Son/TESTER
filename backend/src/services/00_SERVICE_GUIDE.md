# Service Layer 메모

비즈니스 로직 처리. API랑 DB/AI 사이의 중간 다리 역할.

## 서비스 목록

### TestGeneratorService
- 오케스트레이터 역할.
- 언어 전략 가져오고 → 검증하고 → 프롬프트 만들어서 → GeminiService 호출함.
- 캐시 체크도 여기서 수행.

### GeminiService
- Google Gemini API 호출 담당.
- `@retry` 붙여놔서 실패하면 몇 번 더 시도함.
- `CacheService` 써서 똑같은 요청은 AI 안 부르고 캐시된 거 리턴 (돈 아낌).
- **스트리밍**: `generate_content_stream()`으로 Chunk 단위로 받아서 SSE로 전달.

### CacheService
- Redis 래퍼.
- 키 생성 로직: SHA256 해시 사용해서 키 길이 일정하게 만듦.
- TTL 정책:
  - Gemini 응답: 2시간 (길게)
  - 유저 히스토리: 30분 (짧게)
  - 검증 규칙: 24시간
- **Fail-Safe**: Redis 연결 실패 시에도 서비스는 계속 동작 (캐시 없이).

### ExecutionService
- Worker VM이랑 통신 담당.
- `httpx` 비동기 클라이언트 사용.
- `WORKER_URL` 환경변수 쓰고, 헤더에 토큰 넣어서 보냄.
- 타임아웃: 60초 (테스트 실행 시간 고려).

### SupabaseService
- DB 클라이언트 관리 (Singleton).
- **Service Role 사용**: `SUPABASE_SERVICE_ROLE_KEY`를 사용하여 RLS를 우회, 관리자 권한으로 데이터를 저장/관리함.
- **직접 사용하지 않음**: `GenerationRepository` 같은 Repository Layer를 통해서만 접근.
- Lazy Loading 적용됨 (앱 시작 시점 Crash 방지).

---

## Repository Layer

### GenerationRepository
- 생성 이력(`generation_history`) 테이블 전담.
- `generated_code`, `input_code` 포함한 데이터 저장/조회.
- **암호화 담당**: `EncryptionService` 사용하여 민감 데이터 암호화/복호화 수행.
  - **Fail-Closed 정책**: 키가 없거나 암호화 실패 시 절대 평문을 저장하지 않고 에러를 발생시킴.
- **복호화 실패 처리**: DB에서 읽은 데이터 복호화 실패 시 해당 항목은 건너뛰고 로그만 남김 (corrupted data).

### EncryptionService
- **위치**: `utils/security.py`
- **알고리즘**: Fernet (대칭키 암호화)
- **키 관리**: `DATA_ENCRYPTION_KEY` 환경 변수에서 로드 (Base64 인코딩된 32바이트 키)
- **Fail-Closed 보장**:
  - 키 누락 → `RuntimeError` 발생
  - 암호화 실패 → 평문 반환 대신 에러 발생
  - 복호화 실패 → 평문 반환 대신 에러 발생
- **안전성**: 절대 민감 데이터가 평문으로 DB에 저장되지 않음.

---

## 의존성 흐름
```
API → TestGenerator → LanguageFactory / Gemini → Cache / Repository → Supabase
                                                     ↓
                                              EncryptionService
```
