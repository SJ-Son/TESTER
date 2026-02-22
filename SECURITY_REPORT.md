# 보안 점검 보고서

## 1. 정적 분석 및 구성 (Static Analysis & Configuration)

### 🚨 심각도: HIGH
💡 **취약점:** **Backend: Missing Critical Secret Validation** (`backend/src/config/settings.py`)
- `SUPABASE_JWT_SECRET`이 설정되지 않아도 애플리케이션이 시작될 수 있었으며, 이는 런타임에 인증 실패를 유발하거나 잘못된 보안 상태를 초래할 수 있음.

🎯 **영향:**
- 배포 시 중요 시크릿 누락을 조기에 감지하지 못해, 인증 기능이 오작동하거나 보안 설정이 약화된 상태로 서비스가 운영될 위험.

🔧 **수정:**
- `backend/src/config/settings.py`의 `validate_critical_keys` 메서드에 `SUPABASE_JWT_SECRET` 검증 로직 추가.
- `backend/src/main.py`에서 불필요한 런타임 검사 제거 (Startup 시 보장됨).

✅ **검증:**
- `SUPABASE_JWT_SECRET` 환경 변수를 제거하고 서버 시작 시도 시 `RuntimeError` 발생 확인.

---

### 🚨 심각도: HIGH
💡 **취약점:** **Backend: Insecure CORS Configuration** (`backend/src/main.py`)
- `CORSMiddleware`가 모든 오리진(`["*"]`)을 허용하도록 설정되어 있었음.

🎯 **영향:**
- 악의적인 웹사이트가 사용자의 브라우저를 통해 백엔드 API에 무단 요청을 보낼 수 있음 (CSRF 유사 공격 가능성).

🔧 **수정:**
- `allow_origins=["*"]`을 `settings.allowed_origins_list`로 변경하여, 프로덕션 환경에서는 신뢰된 도메인만 허용하도록 제한.

✅ **검증:**
- `backend/src/main.py` 코드 리뷰 및 설정 파일 확인.

---

### 🚨 심각도: MEDIUM
💡 **취약점:** **Worker: Insufficient Sandboxing (AST Bypass)** (`worker/security.py`)
- `SecurityChecker`가 `__mro__`, `__subclasses__` 등의 클래스 계층 구조 탐색 속성을 완벽히 차단하지 못할 수 있음.

🎯 **영향:**
- 악의적인 사용자가 파이썬의 인트로스펙션 기능을 이용해 샌드박스를 우회하고 시스템 명령어를 실행할 가능성 존재 (단, Docker 컨테이너 격리가 2차 방어선으로 존재).

🔧 **수정:**
- `FORBIDDEN_ATTRIBUTES`에 `__mro__`, `__module__`, `__loader__` 추가하여 방어 강화.

✅ **검증:**
- `worker/security.py` 코드 확인.

---

## 2. 인프라 보안 (Infrastructure Security)

### 🚨 심각도: MEDIUM
💡 **취약점:** **Worker: Missing Secure Build Definition** (`worker/Dockerfile`)
- 워커 서비스 자체에 대한 명시적인 `Dockerfile`이 부재하거나 `setup.example.sh`에 의존적이었음. 루트 권한으로 실행될 가능성 높음.

🎯 **영향:**
- 워커 서비스가 침해당할 경우 호스트 시스템(Docker Socket)에 대한 루트 권한 접근이 용이해짐. 재현 가능한 빌드 환경 부재.

🔧 **수정:**
- `worker/Dockerfile` 생성: `python:3.12-slim` 기반, 비특권 사용자(`worker`) 생성(단, Docker 소켓 접근을 위해 실행 시 그룹 매핑 필요), 헬스체크 추가.

✅ **검증:**
- `docker build -t worker-service worker/` 명령어 실행 성공 확인.

---

## 3. 의존성 (Dependencies)

### 📝 참고
- `backend/poetry.lock` 및 `worker/requirements.txt`의 주요 라이브러리(`fastapi`, `pydantic`, `docker`)는 최신 안정 버전을 유지하고 있음.
- `virtualenv` 업데이트 수행.
