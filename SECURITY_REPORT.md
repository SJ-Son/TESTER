# 보안 분석 보고서

Google Senior Security Engineer로서 수행한 프로젝트 전체 보안 분석 결과 및 조치 사항을 보고합니다.

---

## 🚨 조치 완료된 보안 이슈 (CRITICAL / HIGH)

### 1. `python-jose` 라이브러리 사용 중단 및 교체
🚨 **심각도:** HIGH
💡 **취약점:** [Deprecated Library] `python-jose`
🎯 **영향:** `python-jose`는 더 이상 유지보수되지 않는 라이브러리로, 향후 보안 취약점이 발견되더라도 패치가 제공되지 않습니다. 이는 JWT 인증 시스템의 잠재적 보안 위협이 될 수 있습니다.
🔧 **수정:** `backend/pyproject.toml` 및 `backend/src/main.py`에서 `python-jose` 의존성을 제거하고, 활발히 유지보수되는 `PyJWT`로 교체하였습니다.
✅ **검증:** `pytest backend/` 및 `backend/tests/security/test_jwt_decode.py`(임시)를 통해 JWT 디코딩 및 인증 로직이 정상 작동함을 확인하였습니다.
📝 **참고:** [PyJWT Documentation](https://pyjwt.readthedocs.io/en/stable/)

### 2. `urllib3` 버전 업데이트
🚨 **심각도:** HIGH
💡 **취약점:** [Outdated Dependency] `urllib3 < 2.0.0`
🎯 **영향:** `urllib3` 1.x 버전은 유지보수 모드이며, 2.0.0 이상 버전에서 제공하는 최신 보안 기능 및 수정 사항이 누락될 수 있습니다. Worker 서비스의 외부 통신 보안에 영향을 줄 수 있습니다.
🔧 **수정:** `worker/requirements.txt`에서 `urllib3`의 버전 제약 조건을 `>=1.26.18,<2.0.0`에서 `>=2.0.0`으로 변경하였습니다.
✅ **검증:** `pip install` 및 `pip check`를 통해 `docker` 라이브러리 등 다른 의존성과의 호환성 충돌이 없음을 확인하였습니다.
📝 **참고:** [urllib3 2.0 Migration Guide](https://urllib3.readthedocs.io/en/latest/v2-migration-guide.html)

---

## ⚠️ 발견된 잠재적 보안 이슈 (조치 필요)

### 3. Worker 정적 분석의 우회 가능성
🚨 **심각도:** MEDIUM
💡 **취약점:** [Insufficient Static Analysis] `worker/security.py`의 AST 기반 검사
🎯 **영향:** 현재의 정적 분석은 `ast.Name` 노드만 검사하므로, `getattr(os, 'system')`과 같은 동적 속성 접근이나 `__builtins__`를 이용한 호출 등을 통해 보안 검사를 우회할 수 있습니다. 이는 악성 코드가 Docker 컨테이너 내에서 실행될 위험을 높입니다. (단, Docker 컨테이너 및 gVisor 런타임이 2차 방어선 역할을 수행함)
🔧 **수정 제안:** `visit_Attribute` 등을 추가하여 속성 접근을 검사하고, 위험한 내장 함수 및 속성 접근을 더 엄격하게 차단하는 로직 개선이 필요합니다.
✅ **검증:** 우회 코드를 포함한 테스트 케이스를 추가하여 검출 여부를 확인해야 합니다.

### 4. `WORKER_AUTH_TOKEN` 환경 변수 처리
🚨 **심각도:** MEDIUM
💡 **취약점:** [Insecure Configuration Handling] `worker/main.py`의 `os.getenv` 사용
🎯 **영향:** `WORKER_AUTH_TOKEN`이 설정되지 않았을 때 모듈 레벨에서 `RuntimeError`를 발생시키지만, 환경 변수 로딩 및 검증 로직이 분산되어 있어 일관성이 부족합니다. 또한, `.env` 파일 로딩 지원이 명시적이지 않을 수 있습니다.
🔧 **수정 제안:** Backend와 동일하게 `pydantic-settings`를 도입하여 환경 변수 로딩, 타입 검증, 필수 값 체크를 체계화하고 비밀 값 관리를 강화해야 합니다.

---

### 총평
오늘의 보안 점검 결과, 즉시 조치가 필요한 CRITICAL 및 HIGH 등급의 취약점 2건(`python-jose` 교체, `urllib3` 업데이트)을 성공적으로 수정하였습니다. 발견된 MEDIUM 등급 이슈는 추후 주간 수정 계획에 포함하여 보안성을 지속적으로 강화할 것을 권장합니다.
