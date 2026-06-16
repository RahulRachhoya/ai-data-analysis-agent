# Test System Design for Agentic Data Analysis Sandbox

## Current State (as of branch creation)
- `pytest.ini` configured with `asyncio_mode = auto`
- Existing tests (good foundation):
  - `test_config.py` — multi-provider settings, env loading
  - `test_data_loader.py` — upload/url/api loading, JSON safety, NA handling, stats/preview building
  - `test_sandbox.py` — thorough callback tests (_on_stdout, _on_stderr, _on_result for png/plotly), run_code reset, upload, close/kill behavior. Heavy use of MagicMock + patch for asyncio.to_thread and E2B.
- `conftest.py` — sets sys.path for backend, provides safe dummy env vars (groq + test keys) so pydantic doesn't blow up.

## Designed Test Architecture (Implemented/Extended in this PR)

### Principles
- **Isolation first**: Every node, service, and the graph must be testable without real LLM calls or real E2B sandboxes.
- **Edge case coverage is first class**: Empty data, retry loops, code extraction failures, missing files, length violations, provider fallbacks, viz collection paths, streaming event emission.
- **Mock at the right seam**:
  - LLM: patch or replace `llm.ainvoke` / the bound tools.
  - Sandbox: fully exercised in `test_sandbox.py`; higher levels use `patch("app.services.sandbox.SandboxService")`.
- **Async friendly**: All graph/stream tests use `pytest.mark.asyncio`.
- **Deterministic**: Use fixed thread_id, controlled state transitions.

### Test Layers

1. **Unit — Services** (existing + extended)
   - Data loader edges (already strong): empty content, bad json, NaN/inf handling, numeric_stats with all-null columns, very wide data.
   - Sandbox (existing excellent coverage). Added: missing E2B key early error, canonical filename behavior (indirect).

2. **Unit — Agent Nodes** (new coverage)
   - `analyze_schema_node`
   - `plan_analysis_node`
   - `generate_code_node` (code extraction regex, MAX_CODE_LENGTH truncation)
   - `execute_code_node` (canonical loader, file-not-found edge, error recording into state['errors'])
   - `fix_error_node` (error_count increment, errors list append)
   - `synthesize_node` (error path vs success path)

3. **Integration — Graph** (new)
   - Happy path (schema → plan → code → exec success → synthesize)
   - Error path that triggers exactly 1 retry then success
   - Max retries exhaustion → synthesize receives the final error
   - State threading (messages accumulate, dataset_* fields preserved)

4. **Routes / Streaming** (stretch)
   - `stream_agent_response` event emission order (using mocked agent.astream_events)
   - 404 on bad dataset_id

5. **Property / Parametrized Edges**
   - Various dataset shapes (0 rows, 0 numeric cols, only categoricals, huge preview safety)
   - Malformed LLM outputs for code blocks (```python, plain ```, no fences, extra text)
   - LLM provider not in supported list

### Mock Strategy (examples in new tests)
```python
# In test file
@pytest.fixture
def mock_llm():
    llm = AsyncMock()
    llm.ainvoke.side_effect = [...]  # controlled responses per call
    return llm

# Patch the module-level llm or the factory
with patch("app.agents.nodes.llm", mock_llm):
    ...
```

For sandbox in higher tests:
```python
with patch("app.agents.nodes.SandboxService") as MockSandbox:
    instance = MockSandbox.return_value.__aenter__.return_value
    instance.run_code.return_value = {"stdout": [...], "plots": [], "error": None, ...}
```

### Running Tests
```bash
cd backend
python -m pytest tests/ -q --tb=short
# or with coverage
python -m pytest tests/ --cov=app --cov-report=term-missing
```

### CI / Future
- The pytest.ini is already CI-friendly.
- Recommended: add a GitHub Action that runs `pytest` on backend (with the dummy env from conftest).
- For full end-to-end, use recorded cassettes or a real E2B test key in a protected environment (not on every PR).

## Changes Made in This Improvement Cycle
- Added robust code extraction + length guard (nodes.py)
- Canonical safe data filename in sandbox execution (prevents generated-code quoting bugs)
- Error accumulation and better provider error messages
- Early E2B key check in sandbox.start
- Reorganized all loose root *.md into docs/
- Added this design doc + expanded test coverage for the agent core (new test file(s) exercising nodes + graph paths)

This brings the project from "some service tests" to a proper layered test system focused on the complex LangGraph + self-healing loop that is the heart of the value.
