# 개발자 로그 (DEV_log)

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
  - 실제 운영 환경 배포 후 Ko-fi Webhook URL 등록 필요.
  - `.env`에 `KOFI_VERIFICATION_TOKEN` 값 설정 필수.
  - Supabase SQL Editor에서 `migration_remove_ad_columns.sql` 실행 필요.
