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

2024-05-22 - [FastAPI Serialization]
Learning: FastAPI의 기본 JSONResponse는 편의성은 좋으나 성능상 병목이 될 수 있음. 특히 리스트 조회 API에서 ORJSON 교체만으로도 큰 이득을 봄. Action: 향후 모든 데이터 집약적 API 프로젝트 초기 설정 시 ORJSONResponse를 기본값으로 채택할 것.
