# CodeMate – AI-Powered Code Debugging Agent

CodeMate is an artificial intelligence code debugger app, which assists in bug detection, explanation of errors and generating fixed code through Google's Gemini API.
Developed with **FastAPI, React, Python AST, Ruff, and Gemini**, CodeMate offers a combination of static code analysis and AI-powered debugging.---
## Features
- **AI-Powered Debugging:** Detecting and explaining bugs and errors and suggesting fixed code through Google's Gemini API.
- **Static Code Analysis:** Detection of syntax errors through Python AST before AI debugging.
- **Lint Inspection:** Code quality and common mistakes checking through integration with Ruff.
- **Fix Validation:** Syntax validation of AI-generated fixes in Python.
- **Iterative Fix Refinement:** Retry invalid fixes automatically up to two times.
- **Interactive Frontend:** Submit code and debug it using React-based frontend.
- **REST API:** Back-end developed with FastAPI.
- **Backend Testing:** Automated testing of API endpoints, error handling and fix refinement process.
## Tech Stack
| Technology Type | Technologies |
|---|---|
| Frontend     | React.js, JavaScript, CSS |
| Backend      | Python, FastAPI |
| AI API       | Google Gemini API |
| Static Analysis | Python AST, Ruff |
| Validation   | Pydantic |
| Testing      | Pytest, HTTPX |
| Development  | VS Code, Git, GitHub |
## Architecture
```text
     
                         Developer
                              |
                              v
                      React Frontend
                              |
                              v
                  FastAPI Backend
                      +--------+
                      |        |
                      v        v
           Code Inspector   AI Agent
                      |        |
                 Python AST    v
                      |        v
                      Ruff     Gemini API
                      |        |
                      |    Bug Analysis
                      |    Suggested Fix
                      |        |
                      |        v
                      |    Fix Validation
                      |        |
                      |    +---+----+
                      |    |          |
                      |  Valid       Invalid
                      |    |          |
                      |    |    Refinement
                      |    |   (Max 2)
                      +----+----------+
                              |
                              v
                      JSON Response
                              |
                              v
                      React Frontend
```

## Project Structure

```text
CodeMate/
│
├── backend/
│   ├── main.py
│   ├── agent.py
│   ├── code_inspector.py
│   ├── requirements.txt
│   │
│   └── tests/
│       ├── test_main.py
│       └── test_agent.py
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   └── package.json
│
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

Make sure you have installed:

- Python 3.10+
- Node.js and npm
- Git
- A Google Gemini API key

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/CodeMate.git
cd CodeMate
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Set Up the Backend

Navigate to the backend directory:

```powershell
cd backend
```

Create a virtual environment:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```### 3. Configure Environment Variables

Create a `.env` file inside the `backend` directory:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Get your API key from [Google AI Studio](https://aistudio.google.com/apikey).

**Important:** Never commit your `.env` file or expose your API key publicly.

### 4. Start the Backend Server

From the `backend` directory, run:
```powershell
python -m uvicorn main:app --reload
```

Backend will be available at:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### 5. Configure Frontend

Open another terminal:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
```

Start React server for development:

```powershell
npm run dev
```

Frontend should be available at:

```text
http://localhost:5173
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Information about the API |
| GET | `/health` | Health check |
| POST | `/inspect` | Inspection of Python syntax and linting |
| POST | `/debug` | Code debugging by an AI agent |

### Example Request for Debug Endpoint

**POST** `/debug`

```json
{
  "code": "def add(a, b):\n    return a - b\n\nprint(add(5, 3))",
  "language": "python",
  "error_message": "Expected 8 but got 2"
}
```

Response will contain:

- Bug
- Explanation
- Fix suggestion
- Complexity analysis
- Testing recommendations
- Results of syntax inspection
- Status of fix validation
- Refinement count of agent

## Run tests

Go to the backend folder and activate the virtual environment.

Run:

```powershell
python -m pytest -v
```

**Tests state:** 19 tests passed.

The test suit consists of API functional tests, request validation, error handling and AI agent refinement based on mocked responses from Gemini service.

## Current Limitations

- Guaranteed functionality of generated fixes cannot yet be assured by means of isolated code execution.
- Python Abstract Syntax Tree and Ruff inspections do not cover all kinds of logical bugs.
- Suggestion made by AI should always be considered beforehand.
- Availability of Gemini API and its performance.

## Possible Improvements in the Future

- Isolated code execution in a Docker container.
- Automatic tests of suggested fixes.
- Ability to use the tool in other programming languages.
- Better code editor with syntax highlighting.
- History and debugging of the code.
- Deployment into the production.

## Author

**Priyanjal Rathore**

B.Tech – Computer Science Engineering

[GitHub](https://github.com/YOUR_USERNAME)

---

*CodeMate is an ongoing project aiming at creating an AI debugger that incorporates static code analysis, LLM reasoning, and automatic validation.*