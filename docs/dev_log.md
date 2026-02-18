# 개발자 로그 (DEV_log)

### [2026-02-19] 토큰 시스템 보안 패치 및 Ko-fi 연동
- **작업 요약:**
  - AdMob 제거 및 Ko-fi Webhook(`backend/src/api/v1/kofi.py`) 구현.
  - `TokenService` 리팩토링: 모든 토큰 조작을 Supabase RPC로 이관하여 Atomicity 보장.
  - **Critical Fix:** `initialize_user_wallet` RPC 추가로 Welcome Bonus 중복 지급(Race Condition) 해결.
  - UI 정리: `ControlPanel.vue`에서 Ko-fi 버튼 제거.

- **트러블슈팅:**
  - **이슈:** `claim_daily_bonus` RPC가 일일 보너스 초기화 시 Welcome Bonus를 덮어쓰거나 누락하는 문제.
  - **해결:** `initialize_user_wallet` RPC를 신설하여 "지갑 생성(Welcome Bonus)"과 "일일 보너스 지급"을 명확히 분리하고, 서비스 레이어에서 순차적(Atomic)으로 호출하도록 변경.
  - **이슈:** SQL 마이그레이션 시 `policy already exists` 에러.
  - **해결:** `DROP POLICY IF EXISTS` 구문 추가로 Idempotency 보장.

- **TODO:**
  - Staging 배포 후 실제 Ko-fi Webhook 테스트 필요.

### [2026-02-18] Ko-fi 수익화 전환 작업
- **변경 사항:**
  - AdMob 관련 코드(Backend/Frontend) 전면 제거.
  - Ko-fi Webhook 연동 (`api/v1/kofi.py`) 구현.
  - `python-multipart` 의존성 추가 (Form Data 처리용).
  - DB 스키마 정리 (`daily_ad_count` 등 제거).
- **트러블슈팅:**
  - `ImportError`: `AdRewardLimitError` 제거 후 잔여 import 문으로 인한 테스트 실패 → 모듈 전체 검색하여 제거.
  - `RuntimeError`: FastAPI `Form` 사용 시 `python-multipart` 라이브러리 필요 → `poetry add`로 해결.
  - 통합 테스트 실패: `TokenInfo` 모델 변경(`daily_ad_remaining` 제거)이 테스트 코드에 반영되지 않음 → 테스트 코드 수정.
- **TODO:**
  - 실제 운영 환경 배포 후 Ko-fi Webhook 테스트 필요.
  - `.env`에 `KOFI_VERIFICATION_TOKEN` 값 설정 필수.
  - Supabase SQL Editor에서 `migration_remove_ad_columns.sql` 실행 필요.
