from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.data import router as data_router
from app.routes.agent import router as agent_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown."""
    print("[Agentic Data Analysis Sandbox] Starting up...")
    yield
    print("[Agentic Data Analysis Sandbox] Shutting down...")


app = FastAPI(
    title="Agentic Data Analysis Sandbox",
    description="An AI-powered data analysis platform using LangGraph agents and E2B sandbox",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS - allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(data_router)
app.include_router(agent_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
