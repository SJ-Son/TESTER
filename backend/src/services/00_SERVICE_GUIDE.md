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
- DB 작업.
- `user_id` 기반으로 히스토리 저장/조회.
- Fernet으로 민감 데이터 암호화해서 넣음.

## 의존성 흐름
API -> TestGenerator -> LanguageFactory / Gemini -> Cache / Supabase
