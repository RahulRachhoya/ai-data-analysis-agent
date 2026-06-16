# 🤖 Aether — Professional Agentic Data Analysis

**Enterprise-grade autonomous data analysis platform.**

Upload datasets. Ask natural language questions. Receive precise insights and rich visualizations — executed securely by LangGraph agents inside isolated E2B sandboxes.

Built with **FastAPI + LangGraph** (Python backend) and **Next.js** (professional dark UI).

---

## ✨ Professional Features

- **Autonomous Agent Workflow** — Schema analysis → Planning → Code generation → Secure execution → Self-correction (up to 3 retries) → Synthesis
- **Ultra-Secure Execution** — 100% of Python runs in ephemeral E2B cloud sandboxes. No local `exec()` or eval.
- **Stunning Dark Professional Interface** — Pure black & crisp white typography. Refined typography, generous spacing, elegant components.
- **Rich Visualizations** — Matplotlib/seaborn static images + fully interactive Plotly charts rendered professionally.
- **Flexible Data Sources** — Direct file upload (CSV/JSON), public URL, or authenticated REST API import.
- **Real-time Streaming** — Beautiful SSE-powered live updates of agent thinking, generated code, and results.

## 🎨 New Professional Dark UI

The entire frontend has been completely redesigned for a premium, enterprise feel:

- Deep black backgrounds (#0a0a0a)
- High-contrast white and near-white text
- Clean professional cards, inputs, and code blocks
- Elegant centered landing experience when no data is loaded
- Focused, distraction-free analysis workspace once a dataset is imported

## 📚 Documentation & Previous Improvements

See the `docs/` directory for:
- Deployment guides
- Full test system design
- Historical notes

## 🛠️ Tech Stack

**Backend**
- FastAPI + LangGraph (multi-provider LLM support)
- E2B Code Interpreter
- Pandas / NumPy

**Frontend**
- Next.js 14 + TypeScript + Tailwind
- react-markdown, react-plotly.js, lucide-react

## 🚀 Getting Started

```bash
# Backend
cd backend
cp .env.example .env   # add OPENAI_API_KEY (or GROQ) + E2B_API_KEY
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
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
  src/components/      # refined dark DataSource, Chat, Plots, etc.
docs/                  # guides + test design
```

## 📄 License

MIT
