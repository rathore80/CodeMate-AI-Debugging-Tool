
from types import SimpleNamespace
from fastapi.testclient import TestClient
from code_inspector import inspect_python_code
from google.genai import errors
import json
import main
from code_inspector import validate_fix

client = TestClient(main.app)


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to CodeMate"
    assert response.json()["status"] == "running"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_debug_rejects_empty_code():
    response = client.post(
        "/debug",
        json={
            "code": "",
            "language": "python",
            "error_message": "Test error",
        },
    )

    assert response.status_code == 422


def test_debug_rejects_code_over_limit():
    response = client.post(
        "/debug",
        json={
            "code": "a" * 20001,
            "language": "python",
            "error_message": "",
        },
    )

    assert response.status_code == 422


def test_debug_success(monkeypatch):
    # Fake Gemini's response so the test uses no API credits.
    fake_response = SimpleNamespace(
    text=json.dumps({
        "bug": "Subtraction was used instead of addition.",
        "explanation": "The function returns a - b.",
        "suggested_fix": "return a + b",
        "complexity": "O(1) time and O(1) space",
        "testing": "Check that add(2, 3) returns 5.",
    })
)

    class FakeModels:
        def generate_content(self, **kwargs):
            assert kwargs["model"] == "gemini-3.8-flash"
            return fake_response

    fake_client = SimpleNamespace(models=FakeModels())

    monkeypatch.setattr(main, "client", fake_client)

    response = client.post(
        "/debug",
        json={
            "code": "def add(a, b):\n    return a - b",
            "language": "python",
            "error_message": "Expected 5 but got -1",
        },
    )
    assert response.status_code == 200
    body = response.json()

    assert body["message"] == "Code analyzed successfully"
    assert body["analysis"]["bug"] == (
        "Subtraction was used instead of addition."
    )
    assert body["analysis"]["suggested_fix"] == "return a + b"
    assert response.json()["agent_status"] == "fix_validated"
        
    
    
def test_debug_without_api_client(monkeypatch):
    monkeypatch.setattr(main, "client", None)

    response = client.post(
        "/debug",
        json={
            "code": "print('Hello')",
            "language": "python",
            "error_message": "",
        },
    )

    assert response.status_code == 500
    assert "API key is not configured" in response.json()["detail"]


def test_debug_handles_gemini_api_error(monkeypatch):
    class FakeModels:
        def generate_content(self, **kwargs):
            raise errors.APIError(
                503,
                "Service Unavailable",
                {
                    "error": {
                        "code": 503,
                        "message": "Temporary Gemini outage",
                        "status": "UNAVAILABLE",
                    }
                },
            )

    class FakeClient:
        models = FakeModels()

    monkeypatch.setattr(main, "client", FakeClient())

    response = client.post(
        "/debug",
        json={
            "code": "print(1 + 1)",
            "language": "python",
            "error_message": "",
        },
    )

    assert response.status_code == 503
    assert response.json()["detail"] == (
    "Gemini is temporarily overloaded. "
    "Please retry your request in a few moments."
    )


def test_inspect_valid_python_code():
    result = inspect_python_code(
        "def add(a, b):\n    return a + b"
    )

    assert result["valid"] is True
    assert result["error"] is None
    assert result["line"] is None


def test_inspect_invalid_python_syntax():
    result = inspect_python_code(
        "def add(a, b)\n    return a + b"
    )

    assert result["valid"] is False
    assert result["error"] is not None
    assert result["line"] == 1


def test_inspect_does_not_execute_code():
    code = "raise Exception('This code must not execute')"

    result = inspect_python_code(code)

    assert result["valid"] is True
    assert result["error"] is None

def test_debug_passes_syntax_inspection_to_gemini(monkeypatch):
    captured = {}

    class FakeModels:
        def generate_content(self, **kwargs):
            captured["contents"] = kwargs["contents"]

            return SimpleNamespace(
                text=json.dumps({
                    "bug": "Subtraction instead of addition",
                    "explanation": "The function subtracts b from a.",
                    "suggested_fix": "return a + b",
                    "complexity": "O(1) time and O(1) space",
                    "testing": "Check add(2, 3) == 5",
                })
            )

    class FakeClient:
        models = FakeModels()

    monkeypatch.setattr(main, "client", FakeClient())

    response = client.post(
        "/debug",
        json={
            "code": "def add(a, b)\n    return a + b",
            "language": "python",
            "error_message": "Syntax error",
        },
    )

    assert response.status_code == 200
    assert "Python syntax and lint inspection:" in captured["contents"]
    assert '"valid": false' in captured["contents"]
    assert '"line": 1' in captured["contents"]


def test_inspect_endpoint_valid_code():
    response = client.post(
        "/inspect",
        json={
            "code": "def add(a, b):\n    return a + b",
            "language": "python",
            "error_message": "",
        },
    )

    assert response.status_code == 200
    assert response.json()["syntax_inspection"]["valid"] is True


def test_inspect_endpoint_invalid_code():
    response = client.post(
        "/inspect",
        json={
            "code": "def add(a, b)\n    return a + b",
            "language": "python",
            "error_message": "",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["syntax_inspection"]["valid"] is False
    assert body["syntax_inspection"]["line"] == 1


def test_inspect_endpoint_rejects_other_languages():
    response = client.post(
        "/inspect",
        json={
            "code": "public class Main {}",
            "language": "java",
            "error_message": "",
        },
    )

    assert response.status_code == 400


def test_validate_fix_accepts_valid_python():
    result = validate_fix(
        "def add(a, b):\n    return a + b"
    )

    assert result["syntax_valid"] is True
    assert result["syntax_error"] is None
    assert result["lint"]["available"] is True


def test_validate_fix_rejects_invalid_python():
    result = validate_fix(
        "def add(a, b)\n    return a + b"
    )

    assert result["syntax_valid"] is False
    assert result["syntax_error"] is not None
    assert result["syntax_error_line"] == 1
