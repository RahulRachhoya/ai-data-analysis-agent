"""Shared fixtures and configuration for tests."""

import os
import sys
from pathlib import Path

# Ensure the backend root is on sys.path so that `from app import ...` works
BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# Point .env lookups to the real .env file for pydantic-settings tests
os.environ.setdefault("LLM_PROVIDER", "groq")
os.environ.setdefault("GROQ_API_KEY", "gsk_test-key-for-testing")
os.environ.setdefault("GROQ_MODEL", "llama-3.3-70b-versatile")
os.environ.setdefault("E2B_API_KEY", "e2b_test-key-for-testing")
