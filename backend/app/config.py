import os
from dotenv import load_dotenv

load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
E2B_API_KEY = os.getenv("E2B_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

DATASETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "datasets")
os.makedirs(DATASETS_DIR, exist_ok=True)

MAX_RETRIES = 3
MAX_CODE_LENGTH = 8000
