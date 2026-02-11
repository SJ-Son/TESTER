# Test Guide 메모

백엔드 테스트 전략 및 사용법 요약.

## 1. 실행 (Poetry)

```bash
# 전체
poetry run pytest tests/ -v

# 특정 파일
poetry run pytest tests/unit/test_execution_service.py -v

# 커버리지 (터미널)
poetry run pytest tests/ --cov=src --cov-report=term-missing

# 커버리지 (HTML)
poetry run pytest --cov=src --cov-report=html
# -> htmlcov/index.html 확인
```

---

## 2. 구조

- `unit/`: **단위 테스트**. DB/API 없이 로직만 검증.
- `integration/`: **통합 테스트**. 실제 DB/API 연동 (Mock 사용 가능).
- `security/`: **보안 테스트**. 인증/암호화/권한 검증.
- `conftest.py`: **Fixture 모음**. (중요)

---

## 3. 주요 Fixture (`conftest.py`)

테스트에 자동 주입되거나 필요시 호출하는 모의 객체들.

### Auto-Use (자동 적용)
- `mock_redis_globally`: Redis 연결 가로채기 (실제 Redis 필요 X).
- `disable_rate_limit`: API 호출 제한 해제 (429 에러 방지).
- **환경 변수**: `GEMINI_API_KEY`, `DATA_ENCRYPTION_KEY` 등 더미 값 주입.

### Manual-Use (직접 호출)
- `client`: `TestClient` 인스턴스. API 요청 보낼 때 사용.
- `mock_user_auth`: 로그인 상태(`test_user`) 시뮬레이션.
- `mock_turnstile_success`: 봇 방지 토큰 검증 무조건 통과.

---

## 4. 전략 (Mocking)

### External API
- **Gemini**: 무조건 Mocking. 비용/속도 문제.
- **Supabase**: Unit 테스트는 Mock, Integration은 실제/에뮬레이터 사용 권장.

---

## 5. 목표 커버리지
- **전체**: 70%+
- **핵심 서비스**: 90%+ (Auth, Execution, Payment 등)
