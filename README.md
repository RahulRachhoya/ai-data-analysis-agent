# 🚀 Deployment

**Recommended:** See [DEPLOYMENT_RENDER.md](./DEPLOYMENT_RENDER.md) for the full free Render.com setup with correct backend URL configuration.

Local development:

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

Open http://localhost:3000
