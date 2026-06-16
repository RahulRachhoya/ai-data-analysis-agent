## Backend Test System & Edge Case Analysis

### Overview
This document describes the test strategy for the FastAPI backend (data import routes, agent orchestration with LangGraph + E2B sandbox, and streaming chat).

The goal is to ensure APIs "work as expected" under normal operation **and** a wide range of edge/failure cases.

Tests are located in `backend/tests/`. We use:
- `pytest` + `pytest-asyncio`
- `fastapi.testclient.TestClient` for route-level testing
- Heavy use of `unittest.mock` / `monkeypatch` for external services (httpx, E2B, LLM)
- Parametrized and fixture-driven tests for edge cases

Existing tests (`test_data_loader.py`, `test_sandbox.py`, `test_config.py`) provide good coverage for core services. We added `test_backend_edge_cases.py` for route entry points and additional deep edges.

### Deep Edge Cases Considered

#### 1. File Upload (`POST /api/data/upload`)
- No filename or empty UploadFile (Pydantic 422 before custom handler)
- Unsupported extension (txt, etc.)
- Empty file content (b'')
- Malformed JSON (truncated, invalid)
- Malformed CSV (unclosed quotes, bad encoding)
- Binary data presented as CSV/JSON
- Very large files (memory pressure / OOM in pandas)
- Filenames with special characters or path-like components
- CSV/JSON with only headers (0 rows)
- Duplicate column names
- JSON as single object (not array) — current loader wraps it

#### 2. URL Import (`POST /api/data/url`)
- Invalid / unparsable URL
- Connection refused / DNS failure
- HTTP errors (404, 500, rate limit)
- Timeout (hardcoded 30s)
- Large responses causing memory issues
- Content-type lies vs filename extension
- Redirects to non-data content
- Auth-protected URLs (will fail as public only)

#### 3. API Import (`POST /api/data/api`)
- Invalid method
- Malformed headers string (no ":", multiple ":")
- Invalid JSON body for POST
- `response_path` navigation failures (key missing, hit non-dict)
- Response not JSON
- Empty or scalar (not list) data — loader wraps scalars
- Timeouts, network errors, auth failures
- Deeply nested paths

#### 4. Dataset Retrieval (`get_dataset_info`)
- Non-existent dataset_id (returns None → route 404)
- Corrupt on-disk files after save
- Race conditions / concurrent access to DATASETS_DIR
- Disk full or permission errors on save

#### 5. Agent Query / Chat Start (`POST /api/agent/query` + SSE streaming)
- Missing or invalid dataset_id (404 in route, or error event in stream)
- Empty / whitespace-only question
- Dataset exists but file missing on disk (edge in execute_code_node)
- Agent graph errors (LLM failure, sandbox startup failure, code execution error)
- Retry loop (0, 1, max retries) and final error synthesis
- Streaming client disconnect mid-response
- Very long code / stdout causing truncation or large SSE events
- Code generation producing syntax/runtime errors that the self-healing loop must handle
- Empty dataframe edge (0 rows, no numeric columns)
- Problematic column names in generated pandas code
- E2B quota / key errors / network issues inside sandbox

#### 6. Cross-cutting / Systemic
- Missing required fields in Pydantic models (422 validation)
- Exception bubbling vs user-friendly messages
- Top-level side effects in `agents/nodes.py` (LLM creation at import time) — causes test fragility when optional langchain providers are missing
- No size limits or rate limiting on uploads/queries (potential DoS)
- Concurrent queries sharing on-disk datasets
- SSE formatting and heartbeat

### Test Design Principles
- **Isolation**: Mock at the right layer (httpx for imports, get_dataset_info + agent graph for chat, SandboxService for execution).
- **Parametrization**: Many inputs per scenario (good + many bad).
- **Route + Service**: Test both the FastAPI layer (status codes, response shapes) and internal functions.
- **No real secrets**: All LLM/E2B calls mocked.
- **Readable failures**: Clear assert messages on what edge was being tested.

### Running the Tests
```bash
cd backend
python -m pytest tests/ -q --tb=short

# Specific edge cases
python -m pytest tests/test_backend_edge_cases.py -q
```

### Recommended Future Improvements
- Add property-based testing (hypothesis) for data shapes.
- Full integration test with recorded cassettes (vcrpy) or a test E2B key in CI.
- Enforce request size limits in routes.
- Make LLM initialization fully lazy in nodes.py to eliminate import-time provider import errors.
- Add load testing for large uploads and long-running agent sessions.
- Document expected error formats in OpenAPI.

This test system + the existing service tests give strong confidence that the backend APIs behave correctly for both happy paths and the numerous real-world edge cases users will encounter with file uploads and natural-language data questions.
