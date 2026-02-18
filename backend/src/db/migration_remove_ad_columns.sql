-- ============================================================
-- Ko-fi 전환 마이그레이션: 광고 관련 컬럼 제거
-- Supabase SQL Editor에서 실행하세요.
-- ============================================================

-- 1. user_tokens 테이블에서 광고 관련 컬럼 제거
ALTER TABLE public.user_tokens
    DROP COLUMN IF EXISTS daily_ad_count,
    DROP COLUMN IF EXISTS daily_ad_reset_at;

-- 2. 확인
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'user_tokens'
ORDER BY ordinal_position;
