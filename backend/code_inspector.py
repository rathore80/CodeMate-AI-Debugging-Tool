
import ast
import json
import subprocess
import sys


def inspect_python_code(code: str) -> dict:
    """
    Inspect Python code without executing it.

    Checks syntax using ast and code quality using Ruff.
    """
    syntax_result = {
        "valid": True,
        "error": None,
        "line": None,
        "offset": None,
    }

    try:
        ast.parse(code)
    except SyntaxError as exc:
        syntax_result = {
            "valid": False,
            "error": exc.msg,
            "line": exc.lineno,
            "offset": exc.offset,
        }

    try:
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "ruff",
                "check",
                "--output-format",
                "json",
                "--stdin-filename",
                "submitted_code.py",
                "-",
            ],
            input=code,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )

        if process.returncode not in (0, 1):
            lint_result = {
                "available": False,
                "issues": [],
                "error": "Ruff could not complete the inspection.",
            }
        else:
            findings = json.loads(process.stdout or "[]")
            lint_result = {
                "available": True,
                "issues": [
                    {
                        "code": item.get("code"),
                        "message": item.get("message"),
                        "line": item.get("location", {}).get("row"),
                        "column": item.get("location", {}).get("column"),
                    }
                    for item in findings
                ],
                "error": None,
            }

    except (subprocess.TimeoutExpired, OSError, json.JSONDecodeError):
        lint_result = {
            "available": False,
            "issues": [],
            "error": "Ruff inspection failed or timed out.",
        }

    return {
        **syntax_result,
        "lint": lint_result,
    }

def validate_fix(suggested_fix: str) -> dict:
    """
    Validate suggested Python code without executing it.
    """
    inspection = inspect_python_code(suggested_fix)

    return {
        "syntax_valid": inspection["valid"],
        "syntax_error": inspection["error"],
        "syntax_error_line": inspection["line"],
        "lint": inspection["lint"],
    }
