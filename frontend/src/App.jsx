
import { useState } from "react";
import "./App.css";

function App() {
  const [code, setCode] = useState(
    'def add(a, b):\n    return a + b\n\nprint(add(5, 3))'
  );
  const [language, setLanguage] = useState("python");
  const [errorMessage, setErrorMessage] = useState("");
  const [result, setResult] = useState(null);

 
async function handleInspect() {
  setResult({
    type: "info",
    title: "Inspecting code...",
    message: "Sending your code to the FastAPI backend.",
  });

  try {
    const response = await fetch("http://127.0.0.1:8000/inspect", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        code,
        language,
        error_message: errorMessage,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        typeof data.detail === "string"
          ? data.detail
          : "The backend could not inspect your code."
      );
    }

    const inspection = data.syntax_inspection;

    if (inspection.valid) {
      setResult({
        type: "success",
        title: "Syntax is valid!",
        message: "No Python syntax errors were detected.",
      });
    } else {
      setResult({
        type: "error",
        title: `Syntax error on line ${inspection.line ?? "unknown"}`,
        message: inspection.error || "Invalid Python syntax.",
      });
    }
  } catch (error) {
    setResult({
      type: "error",
      title: "Inspection failed",
      message: error.message || "Could not connect to the backend.",
    });
  }
}


 
async function handleDebug() {
  setResult({
    type: "info",
    title: "Analyzing your code...",
    message: "CodeMate is asking Gemini to analyze your code. This may take a few seconds.",
  });

  try {
    const response = await fetch("http://127.0.0.1:8000/debug", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        code,
        language,
        error_message: errorMessage,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        typeof data.detail === "string"
          ? data.detail
          : "The debugging request failed."
      );
    }

    setResult({
      type: "success",
      title: "AI analysis complete",
      message: [
        `Bug: ${data.analysis.bug}`,
        `Explanation: ${data.analysis.explanation}`,
        `Suggested fix: ${data.analysis.suggested_fix}`,
        `Complexity: ${data.analysis.complexity}`,
        `Testing: ${data.analysis.testing}`,
      ].join("\n\n"),
    });
  } catch (error) {
    setResult({
      type: "error",
      title: "Debugging failed",
      message: error.message || "Could not connect to the backend.",
    });
  }
}


  return (
    <main className="app">
      <header className="topbar">
        <a className="brand" href="/">
          <span className="brand-icon">C</span>
          <span>CodeMate</span>
        </a>
        <span className="status">
          <span className="status-dot" />
          AI Debugging Workspace
        </span>
      </header>

      <section className="hero">
        <span className="eyebrow">YOUR AI CODING ASSISTANT</span>
        <h1>Find bugs. Understand code. <span>Build better.</span></h1>
        <p>Inspect your code locally or get AI-powered debugging guidance.</p>
      </section>

      <section className="workspace">
        <div className="panel editor-panel">
          <div className="panel-header">
            <div>
              <span className="panel-label">CODE EDITOR</span>
              <h2>Your code</h2>
            </div>

            <select
              aria-label="Programming language"
              value={language}
              onChange={(event) => setLanguage(event.target.value)}
            >
              <option value="python">Python</option>
              <option value="javascript">JavaScript</option>
              <option value="java">Java</option>
              <option value="cpp">C++</option>
            </select>
          </div>

          <textarea
            className="code-input"
            aria-label="Code editor"
            spellCheck={false}
            value={code}
            onChange={(event) => setCode(event.target.value)}
            placeholder="Paste your code here..."
          />

          <div className="error-field">
            <label htmlFor="error-message">ERROR MESSAGE <span>(optional)</span></label>
            <textarea
              id="error-message"
              className="error-input"
              value={errorMessage}
              onChange={(event) => setErrorMessage(event.target.value)}
              placeholder="Paste the error or traceback here..."
              rows={3}
            />
          </div>

          <div className="actions">
            <button className="button button-secondary" onClick={handleInspect}>
              Inspect Syntax
            </button>
            <button className="button button-primary" onClick={handleDebug}>
              ✦ Debug with AI
            </button>
          </div>
        </div>

        <div className="panel result-panel">
          <span className="panel-label">ANALYSIS</span>
          <h2>Debugging results</h2>

          {!result ? (
            <div className="empty-state">
              <div className="empty-icon">⌘</div>
              <h3>Your results will appear here</h3>
              <p>Inspect your code or ask AI to explain a bug and suggest a fix.</p>
            </div>
          ) : (
            <div className="result-message">
              <span className="result-symbol">✦</span>
              <div>
                <h3>{result.title}</h3>
                <p className="result-text">{result.message}</p>
              </div>
            </div>
          )}

          <div className="feature-list">
            <div><span>01</span><p><strong>Syntax inspection</strong><br />Check Python syntax locally</p></div>
            <div><span>02</span><p><strong>AI analysis</strong><br />Understand bugs and fixes</p></div>
            <div><span>03</span><p><strong>Testing guidance</strong><br />Learn how to verify solutions</p></div>
          </div>
        </div>
      </section>

      <footer>CodeMate · Built to help you write better code</footer>
    </main>
  );
}

export default App;

