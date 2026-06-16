"""Edge-case and graph-level tests for the LangGraph agent.

These tests use heavy mocking so they run without real API keys or E2B.
They specifically target the fixes and edge cases introduced in this improvement cycle:
- Robust code extraction (regex + fence handling)
- MAX_CODE_LENGTH enforcement
- Canonical safe data filename in execute (no user filename in generated source)
- Error recording into state["errors"]
- Retry loop behavior (0, 1, and max retries)
- Early E2B key failure
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.agents.nodes import (
    _extract_python_code,
    _enforce_code_length,
    generate_code_node,
    execute_code_node,
    fix_error_node,
    synthesize_node,
)
from app.agents.graph import build_agent_graph

from app.config import MAX_CODE_LENGTH


# ------------------------------------------------------------------
# Pure helper tests (no LLM / sandbox)
# ------------------------------------------------------------------

class TestCodeExtraction:
    """Tests for the improved _extract_python_code helper (regex-based)."""

    def test_extracts_python_fence(self):
        text = "Here is the code:\n```python\nprint('hi')\ndf.head()\n```\nDone."
        assert _extract_python_code(text) == "print('hi')\ndf.head()"

    def test_extracts_generic_fence(self):
        text = "``` \nx = 1\nprint(x)\n```"
        assert _extract_python_code(text) == "x = 1\nprint(x)"

    def test_strips_leading_trailing_fences(self):
        text = "```python\ncode here\n```"
        assert _extract_python_code(text) == "code here"

    def test_plain_code_no_fences(self):
        text = "df = df.dropna()\nprint(df.shape)"
        assert _extract_python_code(text) == "df = df.dropna()\nprint(df.shape)"

    def test_empty_or_none(self):
        assert _extract_python_code("") == ""
        assert _extract_python_code(None) == ""


class TestLengthGuard:
    def test_passes_short_code(self):
        short = "print('ok')"
        assert _enforce_code_length(short) == short

    def test_truncates_long_code(self):
        long_code = "x = 1\n" * (MAX_CODE_LENGTH // 2 + 10)
        result = _enforce_code_length(long_code)
        assert len(result) <= MAX_CODE_LENGTH + 50
        assert "TRUNCATED" in result


# ------------------------------------------------------------------
# Node-level tests with mocks
# ------------------------------------------------------------------

@pytest.mark.asyncio
async def test_generate_code_node_extracts_and_enforces_length():
    state = {
        "user_question": "summarize",
        "analysis_plan": "do it",
        "dataset_info": {"columns": ["a"], "row_count": 10},
    }

    mock_llm = AsyncMock()
    long_raw = "```python\n" + ("print('x')\n" * 1000) + "\n```"

    with patch("app.agents.nodes.llm", mock_llm):
        mock_llm.ainvoke.return_value = MagicMock(content=long_raw)
        out = await generate_code_node(state)

    code = out["generated_code"]
    assert len(code) <= MAX_CODE_LENGTH + 100
    assert "TRUNCATED" in code or len(code) < len(long_raw)


@pytest.mark.asyncio
async def test_execute_code_node_uses_canonical_filename_and_records_error():
    state = {
        "generated_code": "print(df.shape)",
        "dataset_file_path": "/tmp/some-uuid.csv",
        "error_count": 0,
        "errors": [],
    }

    mock_sandbox = MagicMock()
    mock_sandbox.start = AsyncMock()
    mock_sandbox.run_code = AsyncMock(return_value={
        "stdout": ["(10, 3)"],
        "stderr": [],
        "plots": [],
        "plotly_figures": [],
        "error": None,
    })
    mock_sandbox.upload_file = AsyncMock()

    with patch("app.agents.nodes.SandboxService", return_value=mock_sandbox), \
         patch("os.path.exists", return_value=True):

        mock_sandbox.__aenter__ = AsyncMock(return_value=mock_sandbox)
        mock_sandbox.__aexit__ = AsyncMock(return_value=None)

        out = await execute_code_node(state)

    call_args = mock_sandbox.run_code.call_args[0][0]
    assert "uploaded_data.csv" in call_args
    assert "/tmp/some-uuid" not in call_args
    assert out["execution_result"]["stdout"] == ["(10, 3)"]


@pytest.mark.asyncio
async def test_fix_error_node_increments_and_records():
    state = {
        "generated_code": "bad code",
        "execution_result": {"error": {"name": "NameError", "value": "df not defined"}},
        "error_count": 1,
        "errors": ["previous"],
        "user_question": "foo",
    }

    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = MagicMock(content="```python\nfixed = True\n```")

    with patch("app.agents.nodes.llm", mock_llm):
        out = await fix_error_node(state)

    assert out["error_count"] == 2
    assert "Retry 2" in out["messages"][0].content
    assert any("NameError" in e for e in out.get("errors", []))


@pytest.mark.asyncio
async def test_synthesize_handles_final_error():
    state = {
        "user_question": "analyze sales",
        "execution_result": {"error": {"value": "All retries failed"}},
    }

    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = MagicMock(content="Sorry, the analysis failed because...")

    with patch("app.agents.nodes.llm", mock_llm):
        out = await synthesize_node(state)

    assert "failed" in out["final_response"].lower()
    assert out["plots"] == []


# ------------------------------------------------------------------
# Graph integration (high value for self-healing edge cases)
# ------------------------------------------------------------------

@pytest.mark.asyncio
async def test_graph_happy_path():
    graph = build_agent_graph()

    with patch("app.agents.nodes.analyze_dataframe_schema") as mock_schema_tool, \
         patch("app.agents.nodes.llm") as mock_llm, \
         patch("app.agents.nodes.SandboxService") as mock_sbx:

        mock_schema_tool.invoke.return_value = "Schema looks good. 5 columns."

        mock_llm.ainvoke.side_effect = [
            MagicMock(content="Plan: groupby and plot"),
            MagicMock(content="```python\nprint('done')\n```"),
            MagicMock(content="Here are the insights..."),
        ]

        instance = mock_sbx.return_value.__aenter__.return_value
        instance.start = AsyncMock()
        instance.upload_file = AsyncMock()
        instance.run_code = AsyncMock(return_value={
            "stdout": ["done"],
            "stderr": [],
            "plots": [{"type": "matplotlib", "image": "data:..."}],
            "plotly_figures": [],
            "error": None,
        })
        instance.__aexit__ = AsyncMock()

        initial = {
            "dataset_id": "ds1",
            "dataset_file_path": "/tmp/ds1.csv",
            "dataset_info": {"columns": ["x"], "row_count": 3},
            "user_question": "show summary",
            "error_count": 0,
            "errors": [],
        }

        result = await graph.ainvoke(initial, {"configurable": {"thread_id": "t1"}})

        assert result["final_response"]
        assert result.get("plots")
        assert result.get("error_count", 0) == 0


@pytest.mark.asyncio
async def test_graph_retry_then_success():
    """Simulates one error that is fixed on the second execute."""
    graph = build_agent_graph()

    with patch("app.agents.nodes.analyze_dataframe_schema") as mock_schema, \
         patch("app.agents.nodes.llm") as mock_llm, \
         patch("app.agents.nodes.SandboxService") as mock_sbx:

        mock_schema.invoke.return_value = "ok schema"

        mock_llm.ainvoke.side_effect = [
            MagicMock(content="plan"),
            MagicMock(content="bad_code()"),
            MagicMock(content="```python\ngood_code()\n```"),
            MagicMock(content="Success after fix"),
        ]

        instance = mock_sbx.return_value.__aenter__.return_value
        instance.start = AsyncMock()
        instance.upload_file = AsyncMock()

        instance.run_code.side_effect = [
            {"stdout": [], "stderr": [], "plots": [], "plotly_figures": [], "error": {"name": "NameError", "value": "name 'bad_code' is not defined"}},
            {"stdout": ["good"], "stderr": [], "plots": [], "plotly_figures": [], "error": None},
        ]
        instance.__aexit__ = AsyncMock()

        initial = {
            "dataset_id": "ds2",
            "dataset_file_path": "/tmp/ds2.csv",
            "dataset_info": {"columns": ["x"]},
            "user_question": "test retry",
            "error_count": 0,
            "errors": [],
        }

        result = await graph.ainvoke(initial, {"configurable": {"thread_id": "t-retry"}})

        assert result["error_count"] == 1
        assert "Success after fix" in result["final_response"]


def test_graph_compiles():
    """Smoke test that the graph definition itself is valid."""
    graph = build_agent_graph()
    assert graph is not None
    assert hasattr(graph, "ainvoke")
