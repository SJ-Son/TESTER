# 개발자 작업 로그 (DEV_log)

### [2026-02-15] 작업 메모
- **성능 최적화 (ExecutionService):**
    - **내용:** `ExecutionService`를 Singleton 패턴으로 전환하고 Connection Pooling 적용.
    - **효과:** 인스턴스 재생성 비용 절감 및 DB 연결 관리 효율화.
- **보안 패치 (API Security):**
    - **내용:** API 키 검증 로직에 `secrets.compare_digest` 적용하여 Timing Attack 방지.

### [2026-02-12] 작업 메모
- **트러블슈팅 (History Endpoint 500 Error):**
    - **증상:** `/api/history` 호출 시 500 Internal Server Error 발생.
    - **원인:** `BaseRepository`에서 상속받은 `self.supabase` 속성을 참조했으나, `SupabaseService`가 싱글톤 패턴으로 리팩토링되면서 해당 속성이 제거되고 `self.client` 프로퍼티로 변경됨.
    - **해결:** `BaseRepository` 및 하위 리포지토리의 `self.supabase` 호출을 `self.client` (또는 `self._supabase.client`)로 수정. 재발 방지를 위해 Integration Test (`tests/integration/test_history.py`) 추가.

- **트러블슈팅 (Weekly Usage Display):**
    - **증상:** 프론트엔드 Control Panel에서 주간 사용량이 `undefined / undefined`로 표시됨.
    - **원인:** 백엔드 `/api/user/status` 응답 구조가 `{"quota": {"limit": 30, "used": ...}}` 형태로 중첩되어 있었으나, 프론트엔드 `testerStore.ts`는 `data.weekly_usage`와 같이 평면적으로 접근함.
    - **해결:** Store의 `fetchUserStatus` 함수에서 `data.quota.used`, `data.quota.limit` 등을 파싱하도록 수정.

- **트러블슈팅 (Execution Payload Mismatch):**
    - **증상:** 코드 실행 요청 시 `422 Validation Error` (Field required: code) 발생.
    - **원인:** 프론트엔드 API (`generator.ts`)는 `input_code` 필드를 전송했으나, 백엔드 Pydantic 모델(`ExecutionRequest`)은 `code` 필드를 정의함. 추가로 `ExecutionService.execute_code` 메서드 인자명도 불일치 (`code` vs `input_code`).
    - **해결:** 
        1. 프론트엔드 요청 필드를 `code`로 통일.
        2. 백엔드 `execution.py` 라우터에서 서비스 호출 시 `input_code=payload.code`로 매핑 수정.

- **리팩토링 (Structured Logging & Docstrings):**
    - **Logging:** `src/utils/logger.py`에 `JSONFormatter` 도입. 모든 로그를 JSON 포즈로 출력하며 `trace_id`를 포함하여 요청 추적 용이성 확보. 이모지 제거 및 한글 메시지로 통일.
    - **Docstrings:** Google Python Style Guide를 준수하는 한글 독스트링으로 전체 코드베이스(API, Service, Utils) 문서화 완료.

### [2026-02-10] 작업 메모
- **트러블슈팅 (Pydantic Validation Error):**
    - **증상:** History API 응답 시 `ResponseValidationError` 다수 발생.
    - **원인:** DB에서 조회된 `UUID` 및 `datetime` 객체가 Pydantic 모델의 타입과 엄격하게 일치하지 않거나, ORM 객체 변환 설정(`from_attributes=True`)이 누락됨.
    - **해결:** Pydantic 모델 (`HistoryResponse`) 설정 업데이트 및 필드 타입 정합성 확보.

### [2026-02-09] 작업 메모
- **인프라 (Supabase & Redis):**
    - **이슈:** 초기 기동 시 Redis 연결 실패가 간헐적으로 발생.
    - **해결:** `backoff` 전략을 적용한 재시도 로직 추가 및 헬스 체크 엔드포인트(`/health`) 강화.
    - **배운 점:** `asyncio` 환경에서 `redis-py` 사용 시 커넥션 풀 관리가 중요함.

### [2026-01-30] 작업 메모
- **UI/UX (Dark Mode & Layout):**
    - **이슈:** 다크 모드에서 구글 로그인 버튼 주변에 흰색 아티팩트(Box)가 남는 문제.
    - **해결:** CSS `box-shadow` 및 `border` 속성 미세 조정, 버튼 이미지를 테마에 맞는 에셋으로 교체.
    - **UI:** 사이드바 레이아웃을 반응형으로 개선 (모바일 햄버거 메뉴 적용).
