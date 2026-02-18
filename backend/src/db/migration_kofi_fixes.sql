-- ============================================================
-- Ko-fi Webhook 최적화: 이메일로 사용자 ID 조회
-- ============================================================

-- auth.users 테이블에 접근하기 위해 SECURITY DEFINER 사용
CREATE OR REPLACE FUNCTION public.get_user_id_by_email(p_email TEXT)
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_user_id UUID;
BEGIN
    SELECT id INTO v_user_id
    FROM auth.users
    WHERE email = p_email
    LIMIT 1;

    RETURN v_user_id;
END;
$$;
