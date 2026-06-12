# CodeMap Explorer

**A local Git repository analysis engine with a visual dependency graph and AI-powered code insights.**

CodeMap Explorer scans any local repository, maps file dependencies, and renders an interactive graph. Click any file node to get an AI generated explanation powered by Google Gemini.

---

## Features

-  **Visual Dependency Graph** — See how your files connect via imports and requires
-  **AI Code Explanations** — Click any file for a Gemini-powered summary, purpose, complexity, and key concepts
-  **Language Detection** — Supports Python, JavaScript, TypeScript, Java, Go, Ruby, Rust, and more
-  **Code Metrics** — Lines of code, file size categories, and dependency counts
-  **Interactive UI** — Zoom, pan, minimap, and animated edges in a stunning dark-mode interface

---

## Prerequisites

- **Python 3.10+** — [Download](https://www.python.org/downloads/)
- **Node.js 18+** — [Download](https://nodejs.org/)
- **Google Gemini API Key** — [Get one here](https://aistudio.google.com/apikey)

---

## Setup

### 1. Clone / Download

```bash
cd codemap-explorer
```

### 2. Backend Setup

```bash
cd backend

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your Gemini API key:
#   GEMINI_API_KEY=your_actual_key_here
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

---

## Getting a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the key
5. Paste it into `backend/.env`:
   ```
   GEMINI_API_KEY=your_key_here
   ```

> **Note:** The free tier of Gemini API is sufficient for this application. The AI explanation feature calls `gemini-2.5-flash` (with `gemini-1.5-flash-latest` as a rate-limit fallback) which has generous rate limits.

---

## Running the Application

### Start the Backend (Terminal 1)

```bash
cd backend
source venv/bin/activate  # activate your virtual environment
python main.py
```

The API server starts at **http://localhost:8000**

### Start the Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

The UI opens at **http://localhost:5173**

---

## Usage

1. Open **http://localhost:5173** in your browser
2. Enter the **absolute path** to any local repository (e.g., `/Users/you/projects/my-app`)
3. Click **"Analyze Repository"**
4. Explore the dependency graph:
   - **Zoom** with scroll wheel
   - **Pan** by dragging the background
   - **Click a node** to see AI-powered code insights in the side panel
5. Use the **"Change Repository"** button in the toolbar to analyze a different repo

---

## API Endpoints

| Method | Endpoint        | Description                          |
|--------|-----------------|--------------------------------------|
| POST   | `/api/analyze`  | Analyze a repository and return graph |
| POST   | `/api/explain`  | Get AI explanation for a file         |
| GET    | `/api/health`   | Health check                          |

---

## Tech Stack

### Backend
- **FastAPI** — High-performance Python web framework
- **Uvicorn** — ASGI server
- **GitPython** — Git repository interaction
- **httpx** — Async HTTP client for Gemini API

### Frontend
- **React 18** — UI library
- **Vite** — Build tool
- **React Flow (@xyflow/react)** — Interactive node graph
- **Axios** — HTTP client
- **Lucide React** — Icon library

---

## Screenshots

| Input Screen | Graph View | AI Insights |
|:---:|:---:|:---:|
| <img src="./screenshots/input.png?v=3" alt="Input Screen"> | <img src="./screenshots/graph.png?v=3" alt="Graph View"> | <img src="./screenshots/insights.png?v=3" alt="AI Insights"> |

---

## Troubleshooting

### "Failed to analyze repository"
- Ensure you entered an **absolute path** (e.g., `/Users/you/project`, not `~/project`)
- Make sure the directory exists and contains code files

### AI explanation not working
- Verify your `GEMINI_API_KEY` is set correctly in `backend/.env`
- Check the backend terminal for API error messages

### CORS errors
- Make sure the backend is running on port **8000** and frontend on port **5173**

---

## License

MIT
