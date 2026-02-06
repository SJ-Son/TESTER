# Service Layer 메모

비즈니스 로직 처리. API랑 DB/AI 사이의 중간 다리 역할.

## 서비스 목록

### TestGeneratorService
- 오케스트레이터 역할.
- 언어 전략 가져오고 -> 검증하고 -> 프롬프트 만들어서 -> GeminiService 호출함.

### GeminiService
- Google Gemini API 호출 담당.
- `@retry` 붙여놔서 실패하면 몇 번 더 시도함.
- `CacheService` 써서 똑같은 요청은 AI 안 부르고 캐시된 거 리턴 (돈 아낌).

### CacheService
- Redis 래퍼.
- 키 생성 로직: SHA256 해시 사용해서 키 길이 일정하게 만듦.
- TTL 정책:
  - Gemini 응답: 2시간 (길게)
  - 유저 히스토리: 30분 (짧게)

### ExecutionService
- Worker VM이랑 통신 담당.
- `httpx` 비동기 클라이언트 사용.
- `WORKER_URL` 환경변수 쓰고, 헤더에 토큰 넣어서 보냄.

### SupabaseService
- DB 클라이언트 관리 (Singleton).
- **직접 사용하지 않음**: `GenerationRepository` 같은 Repository Layer를 통해서만 접근.
- Lazy Loading 적용됨 (앱 시작 시점 Crash 방지).

### GenerationRepository
- 생성 이력(`generation_history`) 테이블 전담.
- `generated_code` 포함한 데이터 저장.
- **암호화 담당**: `EncryptionService` 사용하여 민감 데이터 암호화/복호화 수행.


## 의존성 흐름
API -> TestGenerator -> LanguageFactory / Gemini -> Cache / Repository -> Supabase
