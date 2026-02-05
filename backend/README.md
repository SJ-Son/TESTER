# Backend 학습 메모

TESTER 백엔드 아키텍처 및 핵심 로직 정리.

## 아키텍처 개요

### FastAPI & Async IO
- **선택 이유**: AI 서비스 특성상 I/O Bound 작업(Gemini API 대기, DB 조회 등)이 많음. 동기 방식(Flask/Django)보다 비동기 처리가 효율적이라 판단.
- **특징**: `async def`로 정의된 함수들은 이벤트 루프에서 관리됨. 요청 대기 시간에 다른 작업을 처리할 수 있어 처리량(Throughput)이 높음.

### Directory Structure (Layered)
역할별로 확실하게 분리함.
- `api/`: 컨트롤러 역할. 요청/응답 처리만 담당.
- `services/`: 비즈니스 로직. 실제 일(AI 호출, DB 저장)은 여기서 다 함.
- `config/`: 환경 변수 관리 (`pydantic-settings` 사용).

---

## 주요 구현 포인트

### 1. 실시간 스트리밍 (SSE)
- **문제**: LLM 응답이 오래 걸림.
- **해결**: Server-Sent Events 도입.
- **구현**: `src/api/v1/generator.py`에서 `yield`를 사용한 제너레이터 패턴 적용. 한 덩어리(chunk) 만들어질 때마다 바로 클라이언트로 쏴줌.

### 2. 의존성 주입 (Dependency Injection)
- **목적**: 결합도 낮추기 & 테스트 용이성.
- **방법**: `Depends()` 사용.
- **효과**: 테스트 코드 짤 때 `override_dependency`로 Mock 객체를 쉽게 주입할 수 있었음. (DB 없이 테스트 가능)

### 3. Hybrid Architecture (Cloud Run + Worker VM)
- **구조**:
  - Web Server (Cloud Run): 가벼운 API 처리.
  - Worker (GCE VM): 무거운 Docker 실행 담당.
- **이유**: Cloud Run에서는 Docker-in-Docker 실행이 까다롭고 보안상 좋지 않음. 실행 환경을 아예 물리적으로 격리해버림.
- **통신**: `ExecutionService`가 `httpx`로 Worker API 호출. (`WORKER_AUTH_TOKEN`으로 인증)

---

## 셋업 메모

```bash
# 가상환경
python -m venv venv
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt

# 실행 (Reload 모드)
uvicorn src.main:app --reload
```
