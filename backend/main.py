import json
import os
import re
from pathlib import Path

import httpx
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from analyzer import RepoAnalyzer

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="CodeMap Explorer API",
    description="Analyze code repositories and visualize dependency graphs.",
    version="1.0.0",
)

# CORS – allow the Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

analyzer = RepoAnalyzer()

# Server-side state for the explain endpoint
_last_repo_path = None
_last_file_map: dict = {}

# System directories that must never be analyzed
BLOCKED_PATHS = frozenset({
    "/", "/etc", "/usr", "/bin", "/sbin", "/var",
    "/sys", "/proc", "/dev", "/boot", "/lib", "/tmp",
})


def _validate_repo_path(raw_path: str) -> Path:
    """Validate and resolve a repository path, blocking system-critical locations."""
    repo = Path(raw_path).resolve()

    if not repo.is_absolute():
        raise HTTPException(status_code=400, detail="Path must be absolute.")

    repo_str = str(repo)
    for blocked in BLOCKED_PATHS:
        if repo_str == blocked or (
            blocked != "/" and repo_str.startswith(blocked + "/")
        ):
            raise HTTPException(
                status_code=403,
                detail=f"Access denied: '{raw_path}' is a protected system path.",
            )

    if not repo.exists():
        raise HTTPException(
            status_code=400, detail=f"Path does not exist: {raw_path}"
        )

    if not repo.is_dir():
        raise HTTPException(
            status_code=400, detail=f"Path is not a directory: {raw_path}"
        )

    return repo


# --------------- Request / Response models ---------------

class AnalyzeRequest(BaseModel):
    repo_path: str


class ExplainRequest(BaseModel):
    file_id: str


# --------------- Endpoints ---------------

@app.get("/api/health")
async def health():
    """Simple health check."""
    return {"status": "ok"}


@app.post("/api/analyze")
async def analyze(request: AnalyzeRequest):
    """Analyze a local repository and return its dependency graph."""
    global _last_repo_path, _last_file_map

    repo = _validate_repo_path(request.repo_path)

    try:
        graph = analyzer.build_graph(str(repo))

        # Cache file contents server-side for the explain endpoint
        _last_repo_path = str(repo)
        _last_file_map = {
            node["id"]: node.get("data", {}).get("raw_content", "")
            for node in graph["nodes"]
        }

        # Strip raw source code from the response sent to the client
        for node in graph["nodes"]:
            if "data" in node:
                node["data"].pop("raw_content", None)

        return graph
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(exc)}",
        )


@app.post("/api/explain")
async def explain(request: ExplainRequest):
    """Use Google Gemini to explain a code file."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_key_here":
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured. Please set it in the .env file.",
        )

    # Read file content from server-side cache (never sent by the client)
    if not _last_repo_path:
        raise HTTPException(
            status_code=400,
            detail="No repository has been analyzed yet. Please analyze a repository first.",
        )

    content = _last_file_map.get(request.file_id)
    if content is None:
        raise HTTPException(
            status_code=404,
            detail=f"File '{request.file_id}' not found in the last analyzed repository.",
        )

    prompt = (
        "You are a senior software engineer onboarding a new developer.\n"
        f"Analyze this code file named '{request.file_id}' and respond with ONLY "
        "a JSON object in this exact format:\n"
        '{"summary": "2-3 sentence plain-English explanation", '
        '"purpose": "one-line description of what this file does", '
        '"complexity": "low | medium | high", '
        '"key_concepts": ["concept1", "concept2", "concept3"]}\n\n'
        "Here is the code:\n\n"
        f"{content}"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    async def call_gemini(model: str):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        async with httpx.AsyncClient(timeout=30.0) as client:
            return await client.post(url, headers={"x-goog-api-key": api_key}, json=payload)

    try:
        # Try primary model
        response = await call_gemini("gemini-2.5-flash")
        
        # If rate limited, fallback to 1.5 flash-latest which has a separate quota
        if response.status_code == 429:
            fallback = await call_gemini("gemini-1.5-flash-latest")
            if fallback.status_code == 200:
                response = fallback
            else:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate Limit Hit. Primary Error: {response.text} | Fallback Error ({fallback.status_code}): {fallback.text}"
                )
            
        if response.status_code != 200:
            # Check for bad key
            if response.status_code in (400, 401, 403):
                 raise HTTPException(
                     status_code=response.status_code,
                     detail="Your Gemini API Key is invalid or unauthorized. Please check your .env file."
                 )
            raise HTTPException(
                status_code=502,
                detail=f"Google API Error: {response.status_code} - {response.text}",
            )

        data = response.json()

        # Navigate the Gemini response structure to get the text
        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as exc:
            finish_reason = data.get("candidates", [{}])[0].get("finishReason", "UNKNOWN")
            raise HTTPException(
                status_code=502,
                detail=f"Unexpected response structure (Finish Reason: {finish_reason}). Raw data: {json.dumps(data)}",
            )

        # Strip markdown code fences if present (```json ... ``` or ``` ... ```)
        cleaned = text.strip()
        cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned)
        cleaned = re.sub(r"\n?```\s*$", "", cleaned)
        cleaned = cleaned.strip()

        # Parse the JSON
        try:
            result = json.loads(cleaned)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to parse Gemini response as JSON. Raw text: {cleaned}",
            )

        return result

    except HTTPException:
        raise
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Request to Gemini API timed out.",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with Gemini API: {str(exc)}",
        )


# --------------- Entry point ---------------

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
