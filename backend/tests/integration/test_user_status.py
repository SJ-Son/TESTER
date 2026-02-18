"""사용자 상태 API 통합 테스트.

토큰 기반 시스템으로 전환 후의 /api/user/status 엔드포인트를 테스트합니다.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from src.api.v1.deps import get_token_service
from src.config.constants import TokenConstants
from src.main import app
from src.types import TokenInfo


@pytest.mark.asyncio
async def test_get_user_status_success(client, mock_user_auth):
    """
    /api/user/status 엔드포인트가 200 OK와 token_info를 포함한
    올바른 JSON 구조를 반환하는지 테스트합니다.
    """
    mock_service = MagicMock()
    mock_service.get_token_info = AsyncMock(
        return_value=TokenInfo(
            current_tokens=40,
            daily_bonus_claimed=True,
            cost_per_generation=TokenConstants.COST_PER_GENERATION,
        )
    )

    app.dependency_overrides[get_token_service] = lambda: mock_service

    try:
        response = client.get("/api/user/status")

        assert response.status_code == 200
        data = response.json()

        # 인증된 사용자 정보 확인
        assert data["user"]["email"] == "test@example.com"

        # 신규 token_info 응답 확인
        assert data["token_info"]["current_tokens"] == 40
        assert data["token_info"]["daily_bonus_claimed"] is True
        assert data["token_info"]["cost_per_generation"] == TokenConstants.COST_PER_GENERATION

        # 하위 호환성 quota 필드 확인
        assert "quota" in data
        assert data["quota"]["limit"] == 30
    finally:
        app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_get_user_status_zero_tokens(client, mock_user_auth):
    """
    토큰이 0인 경우에도 정상적으로 응답해야 합니다.
    """
    mock_service = MagicMock()
    mock_service.get_token_info = AsyncMock(
        return_value=TokenInfo(
            current_tokens=0,
            daily_bonus_claimed=False,
            cost_per_generation=TokenConstants.COST_PER_GENERATION,
        )
    )

    app.dependency_overrides[get_token_service] = lambda: mock_service

    try:
        response = client.get("/api/user/status")

        assert response.status_code == 200
        data = response.json()
        assert data["token_info"]["current_tokens"] == 0
        assert data["token_info"]["daily_bonus_claimed"] is False
    finally:
        app.dependency_overrides = {}


def test_get_user_status_unauthorized(client):
    """
    인증되지 않은 경우 /api/user/status가 401을 반환하는지 테스트합니다.
    """
    response = client.get("/api/user/status")

    assert response.status_code == 401
