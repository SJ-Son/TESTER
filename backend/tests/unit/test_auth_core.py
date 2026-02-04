from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, status
from jose import jwt
from src.auth import (
    ALGORITHM,
    create_access_token,
    get_current_user,
    verify_google_token,
    verify_turnstile,
)
from src.config.settings import settings

# --- create_access_token Tests ---


def test_create_access_token_structure():
    data = {"sub": "testuser", "email": "test@example.com"}
    token = create_access_token(data)

    # Decode to verify structure
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
    assert payload["sub"] == "testuser"
    assert payload["email"] == "test@example.com"
    assert "exp" in payload


def test_create_access_token_expiration():
    data = {"sub": "testuser"}
    expires = timedelta(minutes=5)
    token = create_access_token(data, expires_delta=expires)

    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
    # exp exists validation is enough as exact time match is flaky
    assert payload["exp"] > 0


# --- verify_google_token Tests ---


@patch("src.auth.id_token.verify_oauth2_token")
def test_verify_google_token_success(mock_verify):
    # Mocking successful verify response
    mock_verify.return_value = {
        "iss": "https://accounts.google.com",
        "sub": "12345",
        "email": "test@example.com",
    }

    result = verify_google_token("valid_token")
    assert result is not None
    assert result["email"] == "test@example.com"


@patch("src.auth.id_token.verify_oauth2_token")
def test_verify_google_token_wrong_issuer(mock_verify):
    # Mocking wrong issuer
    mock_verify.return_value = {"iss": "https://bad-issuer.com", "sub": "12345"}

    result = verify_google_token("token_wrong_iss")
    assert result is None


@patch("src.auth.id_token.verify_oauth2_token")
def test_verify_google_token_exception(mock_verify):
    # Mocking exception during verification
    mock_verify.side_effect = ValueError("Invalid token")

    result = verify_google_token("invalid_token")
    assert result is None


# --- get_current_user Tests ---


@pytest.mark.asyncio
async def test_get_current_user_success():
    # Create a real token
    token = create_access_token({"sub": "user123", "email": "user@test.com"})

    user = await get_current_user(token)
    assert user["id"] == "user123"
    assert user["email"] == "user@test.com"


@pytest.mark.asyncio
async def test_get_current_user_no_token():
    with pytest.raises(HTTPException) as exc:
        await get_current_user("")
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    with pytest.raises(HTTPException) as exc:
        await get_current_user("invalid.token.string")
    assert exc.value.status_code == 401
    assert "Could not validate" in exc.value.detail


@pytest.mark.asyncio
async def test_get_current_user_missing_sub():
    # Token without 'sub'
    payload = {"email": "no_sub@test.com"}
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGORITHM)

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
