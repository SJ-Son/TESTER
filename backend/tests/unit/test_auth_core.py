from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from jose import jwt
from src.auth import (
    get_current_user,
    verify_turnstile,
)
from src.config.settings import settings

# --- get_current_user Tests (Supabase JWT) ---


@pytest.mark.asyncio
async def test_get_current_user_success():
    # Mock settings
    settings.SUPABASE_JWT_SECRET = "test_supabase_secret"

    # Create a valid Supabase-like token
    payload = {
        "sub": "user123",
        "email": "user@test.com",
        "aud": "authenticated",
        "role": "authenticated",
    }
    token = jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256")

    user = await get_current_user(token)
    assert user["id"] == "user123"
    assert user["email"] == "user@test.com"


@pytest.mark.asyncio
async def test_get_current_user_no_secret():
    # Unset secret
    settings.SUPABASE_JWT_SECRET = ""

    with pytest.raises(HTTPException) as exc:
        await get_current_user("any_token")
    assert exc.value.status_code == 500
    assert "Server misconfiguration" in exc.value.detail


@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    settings.SUPABASE_JWT_SECRET = "test_supabase_secret"

    with pytest.raises(HTTPException) as exc:
        await get_current_user("invalid.token.string")
    assert exc.value.status_code == 401
    assert "Could not validate" in exc.value.detail


@pytest.mark.asyncio
async def test_get_current_user_missing_sub():
    settings.SUPABASE_JWT_SECRET = "test_supabase_secret"

    # Token without 'sub'
    payload = {"email": "no_sub@test.com"}
    token = jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256")

    with pytest.raises(HTTPException) as exc:
        await get_current_user(token)
    assert exc.value.status_code == 401
    assert "Invalid token" in exc.value.detail


# --- verify_turnstile Tests ---


@pytest.mark.asyncio
async def test_verify_turnstile_no_secret():
    # Temporarily unset secret key
    original_secret = settings.TURNSTILE_SECRET_KEY
    settings.TURNSTILE_SECRET_KEY = ""

    try:
        result = await verify_turnstile("any_token")
        assert result is True  # Skip verification
    finally:
        settings.TURNSTILE_SECRET_KEY = original_secret


@pytest.mark.asyncio
@patch("src.auth.httpx.AsyncClient")
async def test_verify_turnstile_success(mock_client_cls):
    # Mock httpx response
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": True}

    # post must be awaitable
    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client

    mock_client_cls.return_value = mock_client

    settings.TURNSTILE_SECRET_KEY = "test_secret"
    result = await verify_turnstile("valid_token")
    assert result is True


@pytest.mark.asyncio
@patch("src.auth.httpx.AsyncClient")
async def test_verify_turnstile_failure(mock_client_cls):
    # Mock httpx response with failure
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": False, "error-codes": ["invalid-input-response"]}

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client

    mock_client_cls.return_value = mock_client

    settings.TURNSTILE_SECRET_KEY = "test_secret"
    result = await verify_turnstile("bad_token")
    assert result is False
