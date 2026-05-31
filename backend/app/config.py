import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ---- LLM Provider ----
    llm_provider: str = "openai"

    # ---- OpenAI ----
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    # ---- Anthropic ----
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"

    # ---- Google Gemini ----
    google_api_key: str = ""
    google_model: str = "gemini-2.0-flash"

    # ---- Groq ----
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # ---- AWS Bedrock ----
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    bedrock_model: str = "anthropic.claude-3-sonnet-20240229-v1:0"

    # ---- NVIDIA AI Endpoints ----
    nvidia_api_key: str = ""
    nvidia_model: str = "meta/llama-3.1-70b-instruct"

    # ---- E2B Sandbox ----
    e2b_api_key: str = ""

    # ---- Paths ----
    datasets_dir: str = ""

    # ---- Agent settings ----
    max_retries: int = 3
    max_code_length: int = 8000


# Create a singleton settings instance — loads from .env automatically
settings = Settings()

# Resolve datasets directory
if settings.datasets_dir:
    DATASETS_DIR = settings.datasets_dir
else:
    DATASETS_DIR = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "datasets",
    )
os.makedirs(DATASETS_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Module-level constants for backward compatibility (keeps existing imports
# like `from app.config import GROQ_API_KEY, MAX_RETRIES` working without
# changes to the importing modules).
# ---------------------------------------------------------------------------
LLM_PROVIDER = settings.llm_provider.lower()

OPENAI_API_KEY = settings.openai_api_key
OPENAI_MODEL = settings.openai_model

ANTHROPIC_API_KEY = settings.anthropic_api_key
ANTHROPIC_MODEL = settings.anthropic_model

GOOGLE_API_KEY = settings.google_api_key
GOOGLE_MODEL = settings.google_model

GROQ_API_KEY = settings.groq_api_key
GROQ_MODEL = settings.groq_model

AWS_ACCESS_KEY_ID = settings.aws_access_key_id
AWS_SECRET_ACCESS_KEY = settings.aws_secret_access_key
AWS_REGION = settings.aws_region
BEDROCK_MODEL = settings.bedrock_model

NVIDIA_API_KEY = settings.nvidia_api_key
NVIDIA_MODEL = settings.nvidia_model

E2B_API_KEY = settings.e2b_api_key

MAX_RETRIES = settings.max_retries
MAX_CODE_LENGTH = settings.max_code_length
