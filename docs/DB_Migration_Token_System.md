# 토큰 시스템 DB 마이그레이션 가이드

## 사전 요구사항
- Supabase Dashboard 접근 권한
- `token_schema.sql` 파일 위치: `backend/src/db/token_schema.sql`

## 적용 순서

### 1. Supabase SQL Editor에서 실행

Supabase Dashboard → **SQL Editor** → 새 쿼리에 `token_schema.sql` 내용을 붙여넣고 실행합니다.

> [!WARNING]
> 기존 테이블과 충돌하지 않는지 확인하세요. `user_tokens`, `token_transactions` 테이블이 이미 존재하면 스크립트가 실패합니다 (`IF NOT EXISTS` 포함).

### 2. 생성되는 리소스

| 리소스 | 이름 | 설명 |
|--------|------|------|
| 테이블 | `user_tokens` | 사용자별 토큰 잔액 및 일일 상태 |
| 테이블 | `token_transactions` | 토큰 거래 이력 (로깅) |
| RPC | `deduct_tokens` | 원자적 토큰 차감 |
| RPC | `add_tokens` | 원자적 토큰 적립 |
| RPC | `claim_daily_bonus` | 일일 보너스 수령 |
| RPC | `refund_tokens` | 토큰 환불 |
| RLS | 4개 정책 | 사용자별 데이터 접근 제한 |

### 3. 검증

```sql
-- 테이블 확인
SELECT * FROM user_tokens LIMIT 1;
SELECT * FROM token_transactions LIMIT 1;

-- RPC 테스트 (테스트 사용자 ID 사용)
SELECT deduct_tokens('test-user-id', 10);
SELECT add_tokens('test-user-id', 5, 'test', 'test-ref', '테스트 적립');
SELECT claim_daily_bonus('test-user-id');
```

### 4. 롤백 (필요 시)

```sql
DROP FUNCTION IF EXISTS refund_tokens;
DROP FUNCTION IF EXISTS claim_daily_bonus;
DROP FUNCTION IF EXISTS add_tokens;
DROP FUNCTION IF EXISTS deduct_tokens;
DROP TABLE IF EXISTS token_transactions;
DROP TABLE IF EXISTS user_tokens;
```
