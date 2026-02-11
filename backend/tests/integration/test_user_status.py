from unittest.mock import MagicMock, patch


def test_get_user_status_success(client, mock_user_auth):
    """
    Test verifying the /api/user/status endpoint returns 200 OK
    and the correct JSON structure for an authenticated user.
    """
    # Mock validation dependencies if any

    # Mock Supabase check_weekly_quota to return a specific value
    # The endpoint instantiates SupabaseService() and calls check_weekly_quota
    with patch("src.api.v1.user.SupabaseService") as MockSupabaseService:
        mock_instance = MockSupabaseService.return_value
        mock_instance.check_weekly_quota = MagicMock(return_value=5)

        response = client.get("/api/user/status")

        assert response.status_code == 200
        data = response.json()

        assert data["email"] == "test@example.com"
        assert data["weekly_usage"] == 5
        assert data["weekly_limit"] == 30
        assert data["remaining"] == 25


def test_get_user_status_unauthorized(client):
    """
    Test verifying /api/user/status returns 401 when not authenticated.
    """
    # No mock_user_auth fixture used here
    response = client.get("/api/user/status")

    # Depending on how the dependency is set up, it might be 401 or 403.
    # get_current_user usually raises HTTPException(401) if validation fails
    # or if the header is missing/invalid.
    assert response.status_code == 401
