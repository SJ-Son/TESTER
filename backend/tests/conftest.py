import pytest
import os
from fastapi.testclient import TestClient
from backend.src.main import app
from backend.src.auth import get_current_user, verify_recaptcha

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
    app.dependency_overrides[get_current_user] = lambda: {"id": "test_user", "email": "test@example.com"}
    yield
    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]

@pytest.fixture
def mock_recaptcha_success():
    """Override reCAPTCHA verification for testing."""
    app.dependency_overrides[verify_recaptcha] = lambda: True
    yield
    if verify_recaptcha in app.dependency_overrides:
        del app.dependency_overrides[verify_recaptcha]
