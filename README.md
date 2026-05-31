# 🤖 Agentic Data Analysis Sandbox

An AI-powered data analysis platform that uses **LangGraph agents** to autonomously analyze datasets, write Python code, execute it in a **secure E2B sandbox**, and return insights with rich visualizations.

Built with FastAPI + LangGraph (Python) and Next.js (TypeScript).

---

## ✨ Key Features

| Feature | Description |
|:--------|:------------|
| **🧠 Multi-Step Agent** | LangGraph orchestrates schema analysis → planning → code generation → execution → error handling |
| **🔒 Secure Sandbox** | All code executes in E2B cloud sandboxes — no `exec()` vulnerabilities |
| **📊 Rich Visualizations** | Both matplotlib/seaborn (static) and Plotly (interactive) charts |
| **📥 Flexible Data Import** | Upload CSV/JSON, import from URLs, or fetch from APIs |
| **🔄 Self-Healing** | Agent reads errors and retries with fixes (up to 3 attempts) |
| **⚡ Real-Time Streaming** | SSE-powered streaming shows agent thinking, code, and plots as they're generated |
| **🎨 Beautiful UI** | Dark-themed code blocks, smooth animations, responsive design |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Next.js Frontend                      │
│  ┌─────────┐  ┌──────────┐  ┌────────┐  ┌───────────┐  │
│  │ Upload/  │  │ Chat     │  │ Code   │  │ Plotly/   │  │
│  │ URL/API  │  │ Interface│  │ Viewer │  │ Matplotlib│  │
│  │ Import   │  │ (SSE)    │  │        │  │ Charts    │  │
│  └─────────┘  └──────────┘  └────────┘  └───────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       │ SSE Streaming (text/event-stream)
┌──────────────────────▼──────────────────────────────────┐
│                    FastAPI Backend                        │
│  ┌────────────┐  ┌────────────────┐  ┌───────────────┐  │
│  │ REST API   │  │  LangGraph     │  │ E2B Sandbox   │  │
│  │ (upload,   │  │  Agent Graph   │  │ (secure code  │  │
│  │  query)    │  │                │  │  execution)   │  │
│  └────────────┘  └────────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Agent Workflow (LangGraph)

```
User Question → 📊 Analyze Data Schema → 🧠 Plan Analysis 
    → ✍️ Generate Python Code → 🚀 Execute in E2B Sandbox
    → ✅ Evaluate Result → ❌ [Error: Retry with Fix (max 3)]
    → 📝 Synthesize Final Response with Visualizations
```

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|:-----------|:--------|
| **FastAPI** | Web framework with async support & SSE streaming |
| **LangGraph** | Stateful agent orchestration with cycles/error handling |
| **OpenAI** | LLM for planning, code generation, and synthesis |
| **E2B Sandbox** | Secure, ephemeral cloud Python execution |
| **Pandas/NumPy** | Data manipulation |

### Frontend
| Technology | Purpose |
|:-----------|:--------|
| **Next.js 14** | React framework with App Router |
| **Tailwind CSS** | Utility-first styling |
| **react-markdown** | Markdown rendering for agent responses |
| **react-plotly.js** | Interactive Plotly charts |
| **lucide-react** | Clean icon set |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- Node.js 20+
- An [OpenAI API key](https://platform.openai.com/api-keys)
- An [E2B API key](https://e2b.dev/dashboard) (free tier available)

### 1. Clone & Setup Environment

```bash
# Backend
cd backend
cp .env.example .env
# Edit .env: add your OPENAI_API_KEY and E2B_API_KEY
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### 2. Run Locally

**Option A: Separate terminals**
```bash
# Terminal 1 — Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm run dev
```

**Option B: Docker Compose**
```bash
docker compose up --build
```

The app will be available at **http://localhost:3000**

---

## ☁️ Deployment (Railway)

### Prerequisites
1. Push to a GitHub repository
2. Create a [Railway account](https://railway.app)

### Steps

1. **Create a new Railway project** → Deploy from GitHub repo
2. **Add environment variables** in Railway dashboard:
   - `OPENAI_API_KEY`
   - `E2B_API_KEY`
3. **Railway will auto-detect Dockerfiles** and deploy both services
4. **Add a domain** for your frontend service

Railway automatically:
- Builds and deploys from Dockerfiles
- Provides HTTPS domains
- Manages environment variables
- Scales with demand

---

## 📡 API Reference

### `POST /api/data/upload`
Upload a CSV or JSON dataset.

### `POST /api/data/url`
Import a dataset from a public URL.

### `POST /api/data/api`
Import a dataset from an API endpoint.

### `POST /api/agent/query`
Send a natural language query to the agent.
- **Response**: SSE (Server-Sent Events) stream with events:
  - `thinking` — Agent progress updates
  - `code` — Generated Python code
  - `plot` — Matplotlib PNG or Plotly JSON
  - `stdout` — Code execution output
  - `message` — Final synthesized response
  - `error` — Error messages
  - `done` — Stream complete

### `GET /health`
Health check endpoint.

---

## 📁 Project Structure

```
agentic-data-sandbox/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Environment config
│   │   ├── models/schemas.py    # Pydantic models
│   │   ├── agents/
│   │   │   ├── state.py         # LangGraph state
│   │   │   ├── tools.py         # Custom tools
│   │   │   ├── nodes.py         # Agent nodes
│   │   │   └── graph.py         # Agent graph
│   │   ├── services/
│   │   │   ├── data_loader.py   # Data import service
│   │   │   ├── sandbox.py       # E2B sandbox service
│   │   │   └── viz_converter.py # Visualization helpers
│   │   └── routes/
│   │       ├── data.py          # Data routes
│   │       └── agent.py         # Agent query routes
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx       # Root layout
│   │   │   ├── page.tsx         # Main page
│   │   │   └── globals.css      # Global styles
│   │   ├── components/
│   │   │   ├── DataSourcePanel  # Data import UI
│   │   │   ├── ChatInterface    # Chat + streaming
│   │   │   ├── CodeBlock        # Syntax-highlighted code
│   │   │   ├── PlotViewer       # Chart rendering
│   │   │   └── AgentThinking    # Thinking animation
│   │   └── hooks/
│   │       └── useSSE.ts       # SSE streaming hook
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── README.md
```

---

## 🧠 Skills Demonstrated

| Skill | Implementation |
|:------|:---------------|
| **Multi-Agent Orchestration** | LangGraph state graph with 7 specialized nodes |
| **Tool Use** | Custom tools for schema analysis & result evaluation |
| **Error Handling & Self-Correction** | Conditional edges retry with fixed code (up to 3x) |
| **Secure Code Execution** | E2B sandbox — no `exec()` or `eval()` on the server |
| **RAG-like Data Analysis** | Schema inspection before code generation |
| **Full-Stack Development** | FastAPI + Next.js + Docker + Railway deployment |
| **Real-Time Streaming** | SSE events for agent thinking, code, and results |
| **Data Engineering** | CSV/JSON/URL/API data loading with pandas |

---

## 📄 License

MIT
