import pytest
from fastapi.testclient import TestClient
from src.main import app, format_sse
from unittest.mock import MagicMock, patch

client = TestClient(app)

def test_root_endpoint():
    """Verify the frontend is served."""
    response = client.get("/")
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text
    assert "Datastar" in response.text

def test_format_sse():
    """Verify SSE message formatting for Datastar."""
    event = "datastar-merge-fragments"
    data = '<div id="test">Content</div>'
    formatted = format_sse(event, data)
    assert formatted.startswith(f"event: {event}")
    assert "data: <div" in formatted
    assert formatted.endswith("\n\n")

    # Multiline check
    multi_data = "<div>\n  Line2\n</div>"
    formatted_multi = format_sse(event, multi_data)
    assert "data: <div>" in formatted_multi
    assert "data:   Line2" in formatted_multi

@patch("src.main.gemini_service")
def test_generate_code_api(mock_service):
    """Verify the streaming API works and returns correct Datastar fragments."""
    # Mocking generator
    def mock_generator(*args, **kwargs):
        yield "public class "
        yield "Test {}"
    
    mock_service.generate_test_code.return_value = mock_generator()
    mock_service.model_name = "gemini-3-flash-preview"

    payload = {
        "input_code": "class Test {}",
        "language": "Java",
        "model": "gemini-3-flash-preview",
        "use_reflection": False
    }

    with client.stream("POST", "/api/generate", json=payload) as response:
        assert response.status_code == 200
        # Check if we get SSE events
        content = ""
        for line in response.iter_lines():
            content += line + "\n"
        
        # Verify Datastar Event
        assert "event: datastar-patch-elements" in content
        assert "data: elements <div id=\"output-area\"" in content
        
        # Verify Loading State
        assert "Thinking..." in content
        
        # Verify Logic/Strategy (Java = language-java)
        assert "language-java" in content
        
        # Verify Highlight.js trigger
        assert "hljs.highlightElement" in content
        
        # Verify Content
        assert "public class" in content

@patch("src.main.gemini_service")
def test_validation_error(mock_service):
    """Verify invalid code returns a visible error fragment."""
    # Python strategy rejects simple text usually depending on validation logic
    # But let's assume empty code triggers generic validation if we pass empty string?
    # Our settings/strategies might have specific rules.
    # Python strategy checks `def` or `class` or `import` usually.
    
    payload = {
        "input_code": "Just some random text",
        "language": "Python",
        "model": "gemini-3-flash-preview"
    }
    
    # We expect validation failure from Python strategy if it's strict
    # src/languages/python.py: is_valid check
    
    with client.stream("POST", "/api/generate", json=payload) as response:
        assert response.status_code == 200
        content = response.read().decode()
        # Should contain error message in red box
        assert "bg-red-900" in content
        # assert "유효한 Python 코드가 아닙니다" or similar message
