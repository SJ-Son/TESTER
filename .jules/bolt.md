⚡ Bolt: JSON Serialization & CSP Optimization
NOTE

💡 요약: FastAPI의 기본 응답 클래스를 `ORJSONResponse`로 교체하고, CSP 정책 문자열을 상수로 분리하여 최적화했습니다. 📊 예상 영향: JSON 직렬화 속도 10.42x 향상, 요청 당 문자열 할당 오버헤드 감소.

🔍 발견된 병목 (The Bottleneck)
1.  **JSON 직렬화**: 기본 `json` 라이브러리는 대용량 페이로드(예: 히스토리 목록) 처리 시 속도가 느림.
2.  **문자열 할당**: `security_middleware`에서 복잡한 CSP 정책 문자열을 매 요청마다 새로 생성하고 있었음.

🛠 최적화 내용 (The Optimization)
1.  **ORJSON 적용**: `backend/src/main.py`에서 `default_response_class=ORJSONResponse` 설정. `orjson`은 Rust 기반으로 매우 빠른 직렬화를 제공하며, `datetime`, `numpy` 등을 기본 지원함.
2.  **상수 추출**: `CSP_POLICY`를 `backend/src/config/constants.py`의 `SecurityConstants`로 이동하여 메모리 할당 및 CPU 사이클 절약.

🔬 검증 및 측정 (Measurement)
- **벤치마크**: `backend/scripts/measure_serialization.py` 실행 결과, 50개 히스토리 아이템 직렬화 시 **10.42배 속도 향상** (0.2598s -> 0.0249s / 100 iterations).
- **테스트**: 전체 테스트 슈트 실행 결과 72개 테스트 통과 (Regression 없음).

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
