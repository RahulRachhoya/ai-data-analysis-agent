import base64
import asyncio
from typing import Any


class SandboxService:
    """Service wrapping E2B code interpreter sandbox for secure Python execution."""

    def __init__(self):
        self._sandbox = None
        self._stdout_lines: list[str] = []
        self._stderr_lines: list[str] = []
        self._plots: list[dict] = []
        self._plotly_figures: list[dict] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

    def _on_stdout(self, msg):
        """Callback for stdout from sandbox code execution."""
        # msg is an OutputMessage with .line attribute
        self._stdout_lines.append(msg.line)

    def _on_stderr(self, msg):
        """Callback for stderr from sandbox code execution."""
        self._stderr_lines.append(msg.line)

    def _on_result(self, result):
        """Callback for results (plots, charts) from sandbox code execution."""
        # Check for matplotlib/seaborn PNG plots
        if hasattr(result, "png") and result.png:
            # result.png could be raw bytes or already a base64 string
            if isinstance(result.png, bytes):
                img_b64 = base64.b64encode(result.png).decode("utf-8")
            else:
                img_b64 = result.png
            self._plots.append({
                "type": "matplotlib",
                "image": f"data:image/png;base64,{img_b64}",
            })

        # Check for Plotly figures (saved as inline HTML/data)
        if hasattr(result, "data") and result.data:
            self._plotly_figures.append(result.data)

    async def start(self):
        """Create a new E2B sandbox session with pre-installed packages."""
        from e2b_code_interpreter import Sandbox
        from app.config import E2B_API_KEY

        self._sandbox = await asyncio.to_thread(
            Sandbox, api_key=E2B_API_KEY
        )
        # Pre-install common data science packages
        await asyncio.to_thread(
            self._sandbox.commands.run,
            "pip install pandas numpy matplotlib seaborn plotly scipy scikit-learn -q",
        )
        return self

    async def upload_file(self, local_path: str, sandbox_path: str):
        """Upload a file to the sandbox."""
        if not self._sandbox:
            raise RuntimeError("Sandbox not started")
        with open(local_path, "rb") as f:
            await asyncio.to_thread(
                self._sandbox.files.write, sandbox_path, f.read()
            )

    async def run_code(self, code: str) -> dict[str, Any]:
        """Run Python code in the sandbox and return results."""
        if not self._sandbox:
            raise RuntimeError("Sandbox not started")

        # Reset callbacks state
        self._stdout_lines = []
        self._stderr_lines = []
        self._plots = []
        self._plotly_figures = []

        execution = await asyncio.to_thread(
            self._sandbox.run_code,
            code,
            on_stdout=self._on_stdout,
            on_stderr=self._on_stderr,
            on_result=self._on_result,
        )

        result = {
            "text": execution.text or "",
            "stdout": self._stdout_lines,
            "stderr": self._stderr_lines,
            "error": None,
            "plots": self._plots,
            "plotly_figures": self._plotly_figures,
        }

        if execution.error:
            result["error"] = {
                "name": execution.error.name,
                "value": execution.error.value,
                "traceback": execution.error.traceback,
            }

        return result

    async def close(self):
        """Close the sandbox session."""
        if self._sandbox:
            try:
                await asyncio.to_thread(self._sandbox.kill)
            except Exception:
                pass
            self._sandbox = None


def get_sandbox_service() -> SandboxService:
    """Factory for creating sandbox services."""
    return SandboxService()
