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

## 📍a Documentation

All detailed guides, deployment instructions, and historical fix notes have been moved to the `docs/` directory for better organization:

- [Deployment Guides](docs/)
- [Past Fixes & Notes](docs/)
- [Test System Design](docs/test-system-design.md)

See `docs/README.md` for the full index.

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|:-----------|:--------|
| **FastAPI** | Web framework with async support & SSE streaming |
| **LangGraph** | Stateful agent orchestration with cycles/error handling |
| **OpenAI / Groq / etc** | LLM for planning, code generation, and synthesis (configurable) |
| **E2B Sandbox** | Secure, ephemeral cloud Python execution |
| **Pandas/NumPy** | Data manipulation |

### Frontend
| Technology | Purpose |
|:-----------|:--------|
| **Next.js 14** | React framework with App Router |
| **Tailwind CSS** | Utility-first styling |
| **react-plotly.js** | Interactive Plotly charts |

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- Node.js 20+
- An [OpenAI API key](https://platform.openai.com/api-keys) or Groq etc.
- An [E2B API key](https://e2b.dev/dashboard) (free tier available)

### 1. Clone & Setup Environment

```bash
cd backend
cp .env.example .env
# Edit .env with your keys + LLM_PROVIDER
groq or openai etc.
pip install -r requirements.txt

cd ../frontend
npm install
```

### 2. Run Locally

```bash
# Terminal 1
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2
cd frontend
npm run dev
```

The app will be available at **http://localhost:3000**.

See `docs/` for deployment guides (Railway, Render, etc).

## 📁 Project Structure

```
backend/
├── app/
│   ├── agents/          # LangGraph nodes, state, graph, tools
│   ├── services/        # data_loader, sandbox (E2B), viz
│   ├── routes/
│   └── ...
├── tests/             # pytest (asyncio) - strong coverage on services + new agent edges
├── pytest.ini
└── ...

 docs/                # All guides and design docs
```

## 🧠 Skills Demonstrated

- Multi-Agent Orchestration with LangGraph
- Secure code execution boundary (E2B)
- Self-correction loop (max 3)
- Full stack + real-time SSE

## 📄 License

MIT
