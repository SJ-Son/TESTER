import pytest
from fastapi.testclient import TestClient
from src.auth import get_current_user, verify_turnstile
from src.main import app


@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def setup_overrides():
    """Clear dependency overrides before each test."""
    app.dependency_overrides = {}
    yield
    app.dependency_overrides = {}


@pytest.fixture
def mock_user_auth():
    """Override user authentication for testing."""
    app.dependency_overrides[get_current_user] = lambda: {
        "id": "test_user",
        "email": "test@example.com",
    }
    yield
    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]


@pytest.fixture
def mock_turnstile_success():
    """Override Turnstile verification for testing."""
    app.dependency_overrides[verify_turnstile] = lambda: True
    yield
    if verify_turnstile in app.dependency_overrides:
        del app.dependency_overrides[verify_turnstile]
