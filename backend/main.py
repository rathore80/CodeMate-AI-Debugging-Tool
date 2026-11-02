
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import errors
from pydantic import BaseModel, Field

from agent import analyze_code
from code_inspector import inspect_python_code

load_dotenv()

app = FastAPI(
    title="CodeMate API",
    description="An AI-powered coding and debugging agent",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini client.
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None


# Request and response models.

class DebugRequest(BaseModel):
    code: str = Field(min_length=1, max_length=20000)
    language: str = Field(default="python", max_length=50)
    error_message: str = Field(default="", max_length=10000)


class DebugAnalysis(BaseModel):
    bug: str
    explanation: str
    suggested_fix: str
    complexity: str
    testing: str


class DebugResponse(BaseModel):
    message: str
    language: str
    analysis: DebugAnalysis
    syntax_inspection: dict | None = None
    fix_validation: dict | None = None
    refinement_count: int = 0
    agent_status: str


# Basic endpoints.

@app.get("/")
def home():
    return {
        "message": "Welcome to CodeMate",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


# Local code inspection endpoint.

@app.post("/inspect")
def inspect_code(request: DebugRequest):
    if request.language.strip().lower() != "python":
        raise HTTPException(
            status_code=400,
            detail="Syntax inspection currently supports Python only.",
        )

    inspection = inspect_python_code(request.code)

    return {
        "message": "Code inspection completed",
        "language": request.language,
        "syntax_inspection": inspection,
    }


# AI debugging endpoint.

@app.post("/debug")
def debug_code(request: DebugRequest):

    if client is None:
        raise HTTPException(
            status_code=500,
            detail="Gemini API key is not configured. Check backend/.env",
        )

    # Step 1: Inspect submitted Python code.
    inspection = None

    if request.language.strip().lower() == "python":
        inspection = inspect_python_code(request.code)

    try:
        # Step 2: Ask the AI agent to analyze the code.
        agent_result = analyze_code(
            client,
            request,
            inspection,
        )

        # Step 3: Validate Gemini's structured response.
        analysis = DebugAnalysis.model_validate(
            agent_result["analysis"]
        )

        # Step 4: Return the complete debugging result.
        return DebugResponse(
            message="Code analyzed successfully",
            language=request.language,
            analysis=analysis,
            syntax_inspection=inspection,
            fix_validation=agent_result["fix_validation"],
            agent_status=agent_result["agent_status"],
            refinement_count=agent_result["refinement_count"],
        )

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    except errors.APIError as exc:
        print("Gemini API error type:", type(exc).__name__)
        print("Gemini API error message:", str(exc))

        if exc.code == 503:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Gemini is temporarily overloaded. "
                    "Please retry your request in a few moments."
                ),
            ) from exc

        raise HTTPException(
            status_code=502,
            detail=f"Gemini API request failed: {type(exc).__name__}",
        ) from exc
