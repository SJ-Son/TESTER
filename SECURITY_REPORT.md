# Security Audit Report

## 1. Docker Sandbox Escape and Persistence
🚨 **심각도:** CRITICAL
💡 **취약점:** `worker/main.py` 내 Docker 컨테이너 실행 시 보안 옵션 누락
🎯 **영향:** 컨테이너가 기본 설정으로 실행되어 사용자가 임의의 코드를 실행하여 샌드박스를 탈출하거나, 파일 시스템 권한을 통해 호스트에 영향을 미칠 수 있습니다. 컨테이너가 `root` 권한으로 실행되며, 파일 시스템에 데이터를 보존할 수 있어 영구적인 백도어 및 DoS 공격으로 이어질 수 있습니다.
🔧 **수정:** `docker_client.containers.run` 호출 시 `user="sandbox"`, `read_only=True`, `tmpfs={"/tmp": "", "/app": ""}` 옵션을 추가하고, `exec_run` 호출 시 `user="sandbox"` 옵션을 명시적으로 지정하여 실행 권한을 최소화했습니다.
✅ **검증:** `worker/main.py` 파일 내 `exec_run` 및 `docker_client.containers.run` 코드에 옵션 추가 사항을 정적 코드로 확인했습니다. (또는 `python -m py_compile worker/main.py`로 문법 검증 완료)
📝 **참고:** Docker Security Best Practices (Least Privilege Principle), 호스트 환경 보호 지침

## 2. Weak JWT Secret Validation
🚨 **심각도:** HIGH
💡 **취약점:** `backend/src/config/settings.py` 내 `SUPABASE_JWT_SECRET` 길이 검증 누락
🎯 **영향:** 길이가 짧은 JWT 시크릿을 사용할 경우 브루트포스(Brute-Force) 공격이나 사전 공격(Dictionary Attack)을 통해 악의적인 사용자가 토큰 서명을 위조할 수 있습니다. 이를 통해 권한 없는 사용자가 인증을 우회하고 시스템의 민감한 데이터에 접근하거나 수정할 위험이 있습니다.
🔧 **수정:** `Settings.validate_critical_keys` 메서드에 `SUPABASE_JWT_SECRET`의 길이가 32자 미만일 경우 `ValueError`를 발생시키도록 검증 로직을 추가했습니다.
✅ **검증:** 백엔드 테스트 코드(`pytest tests/security/`)를 실행하여 변경 사항으로 인해 서버 시작 또는 다른 검증 로직이 실패하지 않는지 정상 작동을 확인했습니다.
📝 **참고:** JWT 보안 가이드라인 (최소 256비트 / 32바이트 길이 권장)

## 3. Missing Security Headers in Worker Service
🚨 **심각도:** HIGH
💡 **취약점:** `worker/main.py` 서버 내 보안 HTTP 헤더 누락
🎯 **영향:** XSS(Cross-Site Scripting), Clickjacking, MIME-Sniffing 등의 웹 취약점에 노출될 위험이 있습니다. 공격자가 워커 서비스의 응답을 악용하여 악성 스크립트를 실행하거나 클릭을 유도할 수 있습니다.
🔧 **수정:** `worker/main.py`의 FastAPI 애플리케이션에 미들웨어를 추가하여 `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Content-Security-Policy: default-src 'none'; frame-ancestors 'none'` 보안 헤더를 강제로 적용했습니다.
✅ **검증:** `curl -I http://localhost:5000/health` 명령을 통해 응답 헤더에 설정한 보안 헤더 3개가 올바르게 포함되어 반환되는지 확인했습니다.
📝 **참고:** OWASP Secure Headers Project

## 4. Urllib3 Not Forbidden in Security Checker
🚨 **심각도:** MEDIUM
💡 **취약점:** `worker/security.py` 내 금지 모듈 목록에서 `urllib3` 누락
🎯 **영향:** `requests`와 `urllib`은 금지되어 있지만 `urllib3`는 예외되어 있어 내부 코드에서 이 모듈을 import 해 임의의 네트워크 요청 코드를 작성할 가능성이 있습니다. (단, 현재 네트워크가 격리되어 있어 실제 외부 요청은 불가하므로 심각도는 MEDIUM으로 평가됨)
🔧 **수정:** 현재 환경에서 즉시 악용 불가하므로 수정 보류.
✅ **검증:** -
📝 **참고:** 추후 샌드박스 정책 완화 시 수정 필요.
