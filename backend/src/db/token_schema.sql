-- ============================================================
-- 토큰 시스템 DB 스키마 및 RPC Functions
-- ============================================================

-- UUID 확장 활성화 (이미 활성화되어 있을 수 있음)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- 1. 테이블 정의
-- ============================================================

-- 사용자 토큰 잔액 관리 테이블
CREATE TABLE IF NOT EXISTS public.user_tokens (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    balance INTEGER NOT NULL DEFAULT 0 CHECK (balance >= 0),
    last_daily_bonus_at DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 토큰 거래 내역 (감사 로그)
CREATE TABLE IF NOT EXISTS public.token_transactions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    amount INTEGER NOT NULL,
    type VARCHAR(30) NOT NULL,
    description TEXT,
    balance_after INTEGER NOT NULL,
    reference_id VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 2. RLS 정책
-- ============================================================

ALTER TABLE public.user_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.token_transactions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own tokens"
ON public.user_tokens FOR SELECT TO authenticated
USING (auth.uid() = user_id);

CREATE POLICY "Users can view own transactions"
ON public.token_transactions FOR SELECT TO authenticated
USING (auth.uid() = user_id);

-- ============================================================
-- 3. 인덱스
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_token_tx_user_id
    ON public.token_transactions (user_id);
CREATE INDEX IF NOT EXISTS idx_token_tx_created_at
    ON public.token_transactions (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_token_tx_reference
    ON public.token_transactions (reference_id)
    WHERE reference_id IS NOT NULL;

-- ============================================================
-- 4. RPC Functions (Atomic Operations)
-- ============================================================

-- 토큰 차감 (FOR UPDATE 행 잠금으로 동시성 제어)
CREATE OR REPLACE FUNCTION public.deduct_tokens(
    p_user_id UUID,
    p_amount INTEGER,
    p_description TEXT DEFAULT NULL
)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_current_balance INTEGER;
    v_new_balance INTEGER;
BEGIN
    SELECT balance INTO v_current_balance
    FROM public.user_tokens
    WHERE user_id = p_user_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RETURN json_build_object(
            'success', false,
            'error', 'USER_NOT_FOUND',
            'current_balance', 0
        );
    END IF;

    IF v_current_balance < p_amount THEN
        RETURN json_build_object(
            'success', false,
            'error', 'INSUFFICIENT_TOKENS',
            'current_balance', v_current_balance,
            'required', p_amount
        );
    END IF;

    v_new_balance := v_current_balance - p_amount;
    UPDATE public.user_tokens
    SET balance = v_new_balance, updated_at = NOW()
    WHERE user_id = p_user_id;

    INSERT INTO public.token_transactions
        (user_id, amount, type, description, balance_after)
    VALUES
        (p_user_id, -p_amount, 'generation', p_description, v_new_balance);

    RETURN json_build_object(
        'success', true,
        'deducted', p_amount,
        'current_balance', v_new_balance
    );
END;
$$;

-- 토큰 적립 (UPSERT + 중복 방지)
CREATE OR REPLACE FUNCTION public.add_tokens(
    p_user_id UUID,
    p_amount INTEGER,
    p_type VARCHAR(30),
    p_description TEXT DEFAULT NULL,
    p_reference_id VARCHAR(100) DEFAULT NULL
)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_new_balance INTEGER;
BEGIN
    IF p_reference_id IS NOT NULL THEN
        IF EXISTS (
            SELECT 1 FROM public.token_transactions
            WHERE reference_id = p_reference_id
        ) THEN
            RETURN json_build_object(
                'success', false,
                'error', 'DUPLICATE_TRANSACTION'
            );
        END IF;
    END IF;

    INSERT INTO public.user_tokens (user_id, balance, updated_at)
    VALUES (p_user_id, p_amount, NOW())
    ON CONFLICT (user_id) DO UPDATE
    SET balance = user_tokens.balance + p_amount,
        updated_at = NOW()
    RETURNING balance INTO v_new_balance;

    INSERT INTO public.token_transactions
        (user_id, amount, type, description, balance_after, reference_id)
    VALUES
        (p_user_id, p_amount, p_type, p_description, v_new_balance, p_reference_id);

    RETURN json_build_object(
        'success', true,
        'added', p_amount,
        'current_balance', v_new_balance
    );
END;
$$;

-- 일일 보너스 처리 (조건부 지급)
CREATE OR REPLACE FUNCTION public.claim_daily_bonus(
    p_user_id UUID,
    p_bonus_amount INTEGER DEFAULT 10
)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_last_bonus DATE;
    v_today DATE := CURRENT_DATE;
    v_new_balance INTEGER;
BEGIN
    INSERT INTO public.user_tokens (user_id, balance)
    VALUES (p_user_id, 0)
    ON CONFLICT (user_id) DO NOTHING;

    SELECT last_daily_bonus_at INTO v_last_bonus
    FROM public.user_tokens
    WHERE user_id = p_user_id
    FOR UPDATE;

    IF v_last_bonus = v_today THEN
        SELECT balance INTO v_new_balance
        FROM public.user_tokens
        WHERE user_id = p_user_id;

        RETURN json_build_object(
            'success', false,
            'already_claimed', true,
            'current_balance', v_new_balance
        );
    END IF;

    UPDATE public.user_tokens
    SET balance = balance + p_bonus_amount,
        last_daily_bonus_at = v_today,
        updated_at = NOW()
    WHERE user_id = p_user_id
    RETURNING balance INTO v_new_balance;

    INSERT INTO public.token_transactions
        (user_id, amount, type, description, balance_after)
    VALUES
        (p_user_id, p_bonus_amount, 'daily_bonus', '일일 로그인 보너스', v_new_balance);

    RETURN json_build_object(
        'success', true,
        'added', p_bonus_amount,
        'current_balance', v_new_balance
    );
END;
$$;

-- 토큰 환불 (생성 실패 시)
CREATE OR REPLACE FUNCTION public.refund_tokens(
    p_user_id UUID,
    p_amount INTEGER,
    p_description TEXT DEFAULT '생성 실패로 인한 토큰 환불'
)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_new_balance INTEGER;
BEGIN
    UPDATE public.user_tokens
    SET balance = balance + p_amount,
        updated_at = NOW()
    WHERE user_id = p_user_id
    RETURNING balance INTO v_new_balance;

    IF NOT FOUND THEN
        RETURN json_build_object('success', false, 'error', 'USER_NOT_FOUND');
    END IF;

    INSERT INTO public.token_transactions
        (user_id, amount, type, description, balance_after)
    VALUES
        (p_user_id, p_amount, 'refund', p_description, v_new_balance);

    RETURN json_build_object(
        'success', true,
        'refunded', p_amount,
        'current_balance', v_new_balance
    );
END;
$$;
