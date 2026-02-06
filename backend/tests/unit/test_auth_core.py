from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from src.auth import (
    get_current_user,
    verify_turnstile,
)
from src.config.settings import settings

# --- get_current_user Tests (Supabase Remote Auth) ---


@pytest.mark.asyncio
@patch("src.auth.httpx.AsyncClient")
async def test_get_current_user_success(mock_client_cls):
    # Mock settings
    settings.SUPABASE_URL = "https://test.supabase.co"
    settings.SUPABASE_ANON_KEY = "test_anon_key"

    # Mock httpx response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "user123",
        "email": "user@test.com",
        "role": "authenticated",
    }

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client_cls.return_value = mock_client

    user = await get_current_user("valid_token")
    assert user["id"] == "user123"
    assert user["email"] == "user@test.com"


@pytest.mark.asyncio
async def test_get_current_user_missing_config():
    # Unset config
    settings.SUPABASE_URL = ""
    settings.SUPABASE_ANON_KEY = ""

    with pytest.raises(HTTPException) as exc:
        await get_current_user("any_token")
    assert exc.value.status_code == 500
    assert "Server misconfiguration" in exc.value.detail


@pytest.mark.asyncio
@patch("src.auth.httpx.AsyncClient")
async def test_get_current_user_invalid_token(mock_client_cls):
    settings.SUPABASE_URL = "https://test.supabase.co"
    settings.SUPABASE_ANON_KEY = "test_anon_key"

    # Mock failure response from Supabase
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Invalid token"

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client_cls.return_value = mock_client

    with pytest.raises(HTTPException) as exc:
        await get_current_user("invalid_token")
    assert exc.value.status_code == 401
    assert "Could not validate credentials" in exc.value.detail


@pytest.mark.asyncio
@patch("src.auth.httpx.AsyncClient")
async def test_get_current_user_service_error(mock_client_cls):
    settings.SUPABASE_URL = "https://test.supabase.co"
    settings.SUPABASE_ANON_KEY = "test_anon_key"

    # Mock httpx raising an error (e.g. timeout)
    mock_client = AsyncMock()
    mock_client.get.side_effect = Exception("Connection timeout")
    mock_client.__aenter__.return_value = mock_client
    mock_client_cls.return_value = mock_client

    with pytest.raises(HTTPException) as exc:
        await get_current_user("valid_token")
    assert exc.value.status_code == 401
    assert "Authentication failed" in exc.value.detail


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
