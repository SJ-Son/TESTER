from unittest.mock import AsyncMock, MagicMock

import pytest
from src.api.v1.deps import get_supabase_service
from src.main import app


@pytest.mark.asyncio
async def test_get_user_status_success(client, mock_user_auth):
    """
    /api/user/status 엔드포인트가 200 OK와 인증된 사용자의 올바른 JSON 구조를 반환하는지 테스트합니다.
    """
    # Create mock SupabaseService
    mock_service = MagicMock()
    mock_service.get_weekly_quota = AsyncMock(return_value=5)

    # Override dependency
    app.dependency_overrides[get_supabase_service] = lambda: mock_service

    try:
        response = client.get("/api/user/status")

        assert response.status_code == 200
        data = response.json()

        assert data["user"]["email"] == "test@example.com"
        assert data["quota"]["used"] == 5
        assert data["quota"]["limit"] == 30
        assert data["quota"]["remaining"] == 25
    finally:
        # Clean up
        app.dependency_overrides = {}


def test_get_user_status_unauthorized(client):
    """
    인증되지 않은 경우 /api/user/status가 401을 반환하는지 테스트합니다.
    """
    # No mock_user_auth fixture used here
    response = client.get("/api/user/status")

    # Depending on how the dependency is set up, it might be 401 or 403.
    # get_current_user usually raises HTTPException(401) if validation fails
    # or if the header is missing/invalid.
    assert response.status_code == 401
