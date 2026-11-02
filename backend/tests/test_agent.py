
import json
from types import SimpleNamespace

from agent import analyze_code


# Fake request to avoid creating an actual API request.
class FakeRequest:
    language = "python"
    code = "def add(a, b):\n    return a - b"
    error_message = "Expected 8 but got 2"


# Fake Gemini client.
class FakeModels:
    def __init__(self, responses):
        self.responses = responses
        self.call_count = 0
        self.prompts = []

    def generate_content(self, **kwargs):
        self.prompts.append(kwargs["contents"])

        response = self.responses[self.call_count]
        self.call_count += 1

        return SimpleNamespace(
            text=json.dumps(response)
        )


class FakeClient:
    def __init__(self, responses):
        self.models = FakeModels(responses)


def make_analysis(suggested_fix):
    return {
        "bug": "Subtraction instead of addition",
        "explanation": "The function subtracts instead of adding.",
        "suggested_fix": suggested_fix,
        "complexity": "O(1) time and O(1) space",
        "testing": "Check add(5, 3) == 8",
    }


# Test 1: First suggested fix is valid.
def test_agent_returns_first_valid_fix():

    client = FakeClient([
        make_analysis(
            "def add(a, b):\n    return a + b"
        )
    ])

    result = analyze_code(
        client,
        FakeRequest(),
        {"valid": True, "lint": {"issues": []}},
    )

    assert client.models.call_count == 1
    assert result["refinement_count"] == 0
    assert result["fix_validation"]["syntax_valid"] is True
    assert result["agent_status"] == "fix_validated"


# Test 2: First fix fails, second fix succeeds.
def test_agent_refines_invalid_fix():

    client = FakeClient([
        make_analysis(
            "def add(a, b)\n    return a + b"
        ),
        make_analysis(
            "def add(a, b):\n    return a + b"
        ),
    ])

    result = analyze_code(
        client,
        FakeRequest(),
        {"valid": True, "lint": {"issues": []}},
    )

    assert client.models.call_count == 2
    assert result["refinement_count"] == 1
    assert result["fix_validation"]["syntax_valid"] is True
    assert result["agent_status"] == "fix_validated"

    # Verify Gemini received the previous validation feedback.
    assert "Validation feedback:" in client.models.prompts[1]


# Test 3: All three suggested fixes fail.
def test_agent_stops_after_max_refinements():

    invalid_fix = "def add(a, b)\n    return a + b"

    client = FakeClient([
        make_analysis(invalid_fix),
        make_analysis(invalid_fix),
        make_analysis(invalid_fix),
    ])

    result = analyze_code(
        client,
        FakeRequest(),
        {"valid": True, "lint": {"issues": []}},
    )

    assert client.models.call_count == 3
    assert result["refinement_count"] == 2
    assert result["fix_validation"]["syntax_valid"] is False
    assert result["agent_status"] == "fix_validation_failed"
