⚡ Bolt: HTTP Client Connection Pooling & Singleton Refactor
NOTE

💡 Summary: Refactored `ExecutionService` to reuse a single `httpx.AsyncClient` instance via the Singleton pattern, eliminating repetitive SSL handshakes and TCP connection overhead.
📊 Impact: Reduced `httpx.AsyncClient` instantiations from 1 per request to 1 per application lifecycle. Estimated latency reduction of 50-100ms per execution request (SSL handshake avoidance).

🔍 The Bottleneck
The `ExecutionService.execute_code` method was instantiating a new `httpx.AsyncClient` inside a context manager (`async with`) for every single request.
This caused:
1.  Repeated TCP 3-way handshakes.
2.  Repeated SSL/TLS negotiation (expensive CPU/Network operation).
3.   inability to reuse Keep-Alive connections.

🛠 The Optimization
1.  **Singleton Pattern**: Implemented `__new__` in `ExecutionService` to ensure a single instance exists application-wide.
2.  **Persistent Client**: Initialized `self.client = httpx.AsyncClient(timeout=60.0)` in `__init__`.
3.  **Connection Reuse**: Updated `execute_code` to use `self.client.post(...)`.
4.  **Lifecycle Management**: Added `close()` method and hooked it into `backend/src/main.py`'s shutdown event to gracefully close the connection pool.

🔬 Measurement
Created a benchmark test `tests/test_execution_benchmark.py` that mocks `httpx.AsyncClient`.
*   **Before**: 5 calls to `execute_code` resulted in **5** `AsyncClient` instantiations.
*   **After**: 5 calls to `execute_code` resulted in **1** `AsyncClient` instantiation.
*   **Regression Testing**: Updated `tests/unit/test_execution_service.py` to support the Singleton pattern and verified all 72 tests passed.

📔 Bolt's Journal (Critical Learnings)
2026-02-15 - FastAPI Dependency Injection & Singletons
Learning: FastAPI's `Depends()` creates new instances by default unless cached. While strictly "dependency injection", for heavyweight services like HTTP clients or DB connections, manual Singleton implementation (or `@lru_cache` on the dependency provider) is crucial to prevent resource leaks and performance degradation.
Action: Audit other services (`GeminiService`, `TestGeneratorService`) for similar instantiation patterns and apply Singleton or Lifecycle management where appropriate.

---

⚡ Bolt: JSON Serialization & CSP Construction Optimization
NOTE

💡 요약: FastAPI의 기본 JSONResponse를 고성능 ORJSONResponse로 교체하고, 미들웨어에서 매 요청마다 생성되던 CSP 문자열을 상수로 추출했습니다.
📊 예상 영향: JSON 직렬화 속도 2~10배 향상 (orjson), 미들웨어 CPU 오버헤드 감소.

🔍 발견된 병목 (The Bottleneck)
1. FastAPI는 기본적으로 표준 라이브러리 `json`을 사용하며, 대용량 데이터(코드 생성 결과 등) 직렬화 시 느릴 수 있음.
2. `security_middleware`에서 복잡한 Content-Security-Policy 문자열을 매 요청마다 Python f-string/concatenation으로 재생성하고 있었음.

🛠 최적화 내용 (The Optimization)
1. `orjson` 라이브러리 도입 및 `default_response_class=ORJSONResponse` 설정.
2. `CSP_POLICY` 및 `MAX_CONTENT_LENGTH`를 `final` 상수로 추출하여 런타임 연산 제거.
3. 예외 핸들러 및 미들웨어 응답도 `ORJSONResponse`로 통일.

🔬 검증 및 측정 (Measurement)
- `reproduce_optimization.py` 스크립트로 `ORJSONResponse` 적용 및 CSP 헤더 존재 확인 완료.
- 기존 유닛 테스트(Unit Tests) 통과, 커버리지 유지.

📔 Bolt's Journal (Critical Learnings)
2026-02-16 - [FastAPI Middleware Optimization]
Learning: 미들웨어는 매 요청마다 실행되므로, 단순한 문자열 연산이라도 상수로 추출하는 것이 트래픽이 많을 때 누적 오버헤드를 줄이는 데 중요하다.
Action: 미들웨어 작성 시 불변 데이터는 반드시 모듈 레벨 상수로 선언한다.
