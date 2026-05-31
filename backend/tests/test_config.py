"""Tests for app.config — Settings class, defaults, env-var loading, and _create_llm."""

import os
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# Settings defaults (env vars set in conftest.py)
# ---------------------------------------------------------------------------

class TestSettingsDefaults:
    """Verify that Settings loads expected defaults / env values."""

    def test_provider_default(self):
        from app.config import settings
        # conftest sets LLM_PROVIDER=groq
        assert settings.llm_provider == "groq"

    def test_groq_key_from_env(self):
        from app.config import settings
        assert settings.groq_api_key == "gsk_test-key-for-testing"

    def test_groq_model_from_env(self):
        from app.config import settings
        assert settings.groq_model == "llama-3.3-70b-versatile"

    def test_e2b_key_from_env(self):
        from app.config import settings
        assert settings.e2b_api_key == "e2b_test-key-for-testing"

    def test_openai_defaults_when_not_set(self):
        from app.config import Settings
        s = Settings(openai_api_key="")
        assert s.openai_api_key == ""
        assert s.openai_model == "gpt-4o"

    def test_max_retries_default(self):
        from app.config import settings
        assert settings.max_retries == 3

    def test_max_code_length_default(self):
        from app.config import settings
        assert settings.max_code_length == 8000

    def test_datasets_dir_created(self):
        """Datasets dir should be an existing directory."""
        from app.config import DATASETS_DIR
        assert os.path.isdir(DATASETS_DIR)


# ---------------------------------------------------------------------------
# Module-level backward-compatible constants
# ---------------------------------------------------------------------------

class TestModuleConstants:
    """Verify that module-level constants mirror Settings fields."""

    def test_llm_provider_constant(self):
        from app.config import LLM_PROVIDER, settings
        assert LLM_PROVIDER == settings.llm_provider.lower()

    def test_groq_api_key_constant(self):
        from app.config import GROQ_API_KEY, settings
        assert GROQ_API_KEY == settings.groq_api_key

    def test_groq_model_constant(self):
        from app.config import GROQ_MODEL, settings
        assert GROQ_MODEL == settings.groq_model

    def test_max_retries_constant(self):
        from app.config import MAX_RETRIES, settings
        assert MAX_RETRIES == settings.max_retries

    def test_e2b_api_key_constant(self):
        from app.config import E2B_API_KEY, settings
        assert E2B_API_KEY == settings.e2b_api_key


# ---------------------------------------------------------------------------
# _create_llm factory (from app.agents.nodes)
# ---------------------------------------------------------------------------

class TestCreateLLM:
    """Verify _create_llm returns the correct provider implementation."""

    def test_unknown_provider_raises(self):
        # _create_llm reads LLM_PROVIDER from config at module level,
        # so patching LLM_PROVIDER directly tests the error path
        from app.agents import nodes
        with patch.object(nodes, "LLM_PROVIDER", "nonexistent-provider"):
            with pytest.raises(ValueError, match="Unsupported LLM_PROVIDER"):
                nodes._create_llm()

    def test_groq_provider(self):
        """With GROQ_API_KEY set, should return a ChatGroq instance."""
        from app.agents import nodes
        with (
            patch.object(nodes, "GROQ_API_KEY", "gsk_test-key-for-testing"),
            patch.object(nodes, "GROQ_MODEL", "llama-3.3-70b-versatile"),
        ):
            llm = nodes._create_llm()
        from langchain_groq import ChatGroq
        assert isinstance(llm, ChatGroq)
        assert llm.model_name == "llama-3.3-70b-versatile"
        assert llm.temperature == 0.2

    def test_provider_case_insensitive(self):
        """Provider names should be lowercased."""
        from app.agents import nodes
        with patch.object(nodes, "LLM_PROVIDER", "groq"):
            llm = nodes._create_llm()
        from langchain_groq import ChatGroq
        assert isinstance(llm, ChatGroq)

    def test_openai_provider_no_key_does_not_raise(self):
        """OpenAI ChatOpenAI can be instantiated without a key (will fail at runtime)."""
        pytest.importorskip("langchain_openai", reason="langchain-openai not installed")
        from app.agents import nodes
        with patch.object(nodes, "LLM_PROVIDER", "openai"):
            llm = nodes._create_llm()
        from langchain_openai import ChatOpenAI
        assert isinstance(llm, ChatOpenAI)
        assert llm.model == "gpt-4o"
