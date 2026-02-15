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
