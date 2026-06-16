# 🤖 Aether — Professional Agentic Data Analysis

**Enterprise-grade autonomous data analysis platform.**

Upload datasets. Ask natural language questions. Receive precise insights and rich visualizations — executed securely by LangGraph agents inside isolated E2B sandboxes.

Built with **FastAPI + LangGraph** (Python backend) and **Next.js** (professional dark UI).

**Recommended:** See [DEPLOYMENT_RENDER.md](./DEPLOYMENT_RENDER.md) for the full free Render.com setup with correct backend URL configuration.

---

## ✨ Professional Features

- **Autonomous Multi-Agent Orchestration** — Supervisor + specialists (Profiler, Planner, Coder, Executor, Critic, Suggester, Presenter) with inter-agent communication, heartbeats, waits, step-by-step narrative, and dataset-specific suggestions.
- **Live Interactive Frontend** — Real-time Agent Orchestra panel with pulsing status/heartbeats, clickable suggestion chips that trigger follow-up analyses, progressive plan display.
- **Ultra-Secure Execution** — 100% of Python runs in ephemeral E2B cloud sandboxes. No local `exec()` or eval.
- **Stunning Dark Professional Interface** — Pure black & crisp white typography. Refined typography, generous spacing, elegant components with double-bezel and motivated motion.
- **Rich Visualizations** — Matplotlib/seaborn static images + fully interactive Plotly charts rendered professionally.
- **Flexible Data Sources** — Direct file upload (CSV/JSON), public URL, or authenticated REST API import.
- **Real-time Streaming** — Beautiful SSE-powered live updates of agent thinking, generated code, execution results, and multi-agent status.

## 🎨 New Professional Dark UI + Interactivity

The entire frontend has been completely redesigned for a premium, enterprise feel (with taste-skill upgrades for the multi-agent experience):

- Deep black backgrounds (#0a0a0a)
- High-contrast white and near-white text
- Clean professional cards, inputs, and code blocks
- Elegant centered landing experience when no data is loaded
- Focused, distraction-free analysis workspace once a dataset is imported
- Live Agent Orchestra (pulsing heartbeats for active specialists during orchestration)
- Clickable suggestion chips for seamless follow-up queries

## 📄 Documentation & Previous Improvements

See the `docs/` directory for:
- Deployment guides
- Full test system design
- Multi-agent orchestration details
- Historical notes

## 🛠️ Tech Stack

**Backend**
- FastAPI + LangGraph (multi-provider LLM support)
- E2B Code Interpreter
- Pandas / NumPy

**Frontend**
- Next.js 14 + TypeScript + Tailwind + framer-motion
- react-markdown, react-plotly.js, lucide-react

## 🚀 Getting Started

```bash
# Terminal 1 - Backend
cd backend
cp .env.example .env   # add your GROQ_API_KEY (or OPENAI) + E2B_API_KEY
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd ../frontend
npm install
npm run dev
```

Open **http://localhost:3000** — you will see a refined professional dark interface.

## 📁 Project Structure

```
backend/               # FastAPI + agent logic + tests
frontend/              # Next.js professional dark UI
  src/app/             # layout, page (landing + workspace)
  src/components/      # DataSource, ChatInterface, AgentOrchestra, SuggestionChips, etc.
docs/                  # guides + test design + orchestration notes
```

## 📄 License

MIT
