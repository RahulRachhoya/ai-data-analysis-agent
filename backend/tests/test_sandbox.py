"""Tests for app.services.sandbox — SandboxService callbacks and lifecycle."""

import base64
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.sandbox import SandboxService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def service():
    """A fresh SandboxService for each test."""
    return SandboxService()


# ---------------------------------------------------------------------------
# _on_stdout / _on_stderr callbacks
# ---------------------------------------------------------------------------

class TestStdoutStderrCallbacks:
    """Verify that stdout/stderr callbacks extract the .line attribute."""

    def test_on_stdout_appends_line(self, service):
        msg = MagicMock()
        msg.line = "Hello, stdout!"
        service._on_stdout(msg)
        assert service._stdout_lines == ["Hello, stdout!"]

    def test_on_stderr_appends_line(self, service):
        msg = MagicMock()
        msg.line = "Some warning"
        service._on_stderr(msg)
        assert service._stderr_lines == ["Some warning"]

    def test_on_stdout_multiple_lines(self, service):
        for text in ["line1", "line2", "line3"]:
            msg = MagicMock()
            msg.line = text
            service._on_stdout(msg)
        assert service._stdout_lines == ["line1", "line2", "line3"]

    def test_on_stderr_empty_line(self, service):
        msg = MagicMock()
        msg.line = ""
        service._on_stderr(msg)
        assert service._stderr_lines == [""]


# ---------------------------------------------------------------------------
# _on_result callback
# ---------------------------------------------------------------------------

class TestOnResult:
    """Verify that result callbacks handle PNG / data correctly."""

    def test_png_bytes_gets_base64_encoded(self, service):
        """When result.png is raw bytes, it should be base64-encoded."""
        result = MagicMock()
        raw_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 10
        result.png = raw_bytes
        result.data = None  # no plotly data

        service._on_result(result)

        assert len(service._plots) == 1
        plot = service._plots[0]
        assert plot["type"] == "matplotlib"
        expected_b64 = base64.b64encode(raw_bytes).decode("utf-8")
        assert plot["image"] == f"data:image/png;base64,{expected_b64}"

    def test_png_string_used_directly(self, service):
        """When result.png is already a base64 string, use it directly."""
        result = MagicMock()
        result.png = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk"
        result.data = None

        service._on_result(result)

        assert len(service._plots) == 1
        plot = service._plots[0]
        assert plot["type"] == "matplotlib"
        assert "iVBORw0KGgo" in plot["image"]

    def test_png_none_skipped(self, service):
        """When result.png is None, no plot should be added."""
        result = MagicMock()
        result.png = None
        result.data = None

        service._on_result(result)
        assert service._plots == []

    def test_plotly_data_appended(self, service):
        """When result has .data (not None), it should be appended to plotly_figures."""
        result = MagicMock()
        result.png = None
        result.data = {"type": "plotly", "data": [...]}

        service._on_result(result)
        assert len(service._plotly_figures) == 1
        assert service._plotly_figures[0]["type"] == "plotly"

    def test_missing_png_and_data(self, service):
        """No png and no data → nothing added."""
        result = MagicMock()
        # Remove both attributes
        del result.png
        del result.data

        service._on_result(result)
        assert service._plots == []
        assert service._plotly_figures == []


# ---------------------------------------------------------------------------
# close() method
# ---------------------------------------------------------------------------

class TestClose:
    """Verify sandbox cleanup."""

    @pytest.mark.asyncio
    async def test_close_calls_kill(self, service):
        """close() should call self._sandbox.kill()."""
        service._sandbox = MagicMock()
        mock_kill = MagicMock()
        service._sandbox.kill = mock_kill

        # asyncio.to_thread(func, *args) runs func(*args) in a thread.
        # Patch it to simply call the function directly.
        async def fake_to_thread(func, *args, **kwargs):
            func(*args, **kwargs)

        with patch("asyncio.to_thread", side_effect=fake_to_thread):
            await service.close()

        mock_kill.assert_called_once()
        assert service._sandbox is None

    @pytest.mark.asyncio
    async def test_close_without_sandbox_does_nothing(self, service):
        """close() should be a no-op when _sandbox is None."""
        assert service._sandbox is None
        await service.close()  # should not raise
        assert service._sandbox is None

    @pytest.mark.asyncio
    async def test_close_kill_error_swallowed(self, service):
        """If kill() raises, close() should catch it and still clear _sandbox."""
        service._sandbox = MagicMock()
        service._sandbox.kill = MagicMock(side_effect=RuntimeError("Kill failed"))

        with patch("asyncio.to_thread", new_callable=AsyncMock, side_effect=RuntimeError("Kill failed")):
            await service.close()
        assert service._sandbox is None


# ---------------------------------------------------------------------------
# run_code() — state reset before execution
# ---------------------------------------------------------------------------

class TestRunCode:
    """Verify that run_code resets callback state and returns expected shape."""

    @pytest.mark.asyncio
    async def test_run_code_resets_state(self, service):
        """Calling run_code should clear previous callback accumulators."""
        # Set some pre-existing state
        service._stdout_lines = ["old stdout"]
        service._stderr_lines = ["old stderr"]

        # Mock the sandbox so run_code returns without real execution
        service._sandbox = MagicMock()
        fake_execution = MagicMock()
        fake_execution.text = "done"
        fake_execution.error = None
        service._sandbox.run_code = MagicMock(return_value=fake_execution)

        with patch("asyncio.to_thread", new_callable=AsyncMock, return_value=fake_execution):
            result = await service.run_code("print('hello')")

        # State should have been reset
        assert service._stdout_lines == []
        assert service._stderr_lines == []
        assert service._plots == []
        assert service._plotly_figures == []

        # Result shape
        assert result["text"] == "done"
        assert result["error"] is None
        assert result["stdout"] == []
        assert result["stderr"] == []

    @pytest.mark.asyncio
    async def test_run_code_without_sandbox_raises(self, service):
        """run_code should raise RuntimeError when sandbox not started."""
        with pytest.raises(RuntimeError, match="Sandbox not started"):
            await service.run_code("print('x')")


# ---------------------------------------------------------------------------
# upload_file
# ---------------------------------------------------------------------------

class TestUploadFile:
    """Verify file upload delegates to files.write."""

    @pytest.mark.asyncio
    async def test_upload_file_without_sandbox_raises(self, service, tmp_path):
        """upload_file should raise RuntimeError when sandbox not started."""
        f = tmp_path / "test.csv"
        f.write_text("a,b\n1,2")
        with pytest.raises(RuntimeError, match="Sandbox not started"):
            await service.upload_file(str(f), "remote/test.csv")

    @pytest.mark.asyncio
    async def test_upload_file_calls_files_write(self, service, tmp_path):
        """upload_file should call files.write with binary content."""
        f = tmp_path / "test.csv"
        f.write_text("a,b\n1,2")

        service._sandbox = MagicMock()
        service._sandbox.files.write = MagicMock()

        with patch("asyncio.to_thread", new_callable=AsyncMock) as mock_to_thread:
            await service.upload_file(str(f), "remote/test.csv")

        # Verify asyncio.to_thread was called with files.write
        mock_to_thread.assert_awaited_once()
        args, _ = mock_to_thread.await_args
        assert args[0] == service._sandbox.files.write
        assert args[1] == "remote/test.csv"
        assert isinstance(args[2], bytes)
