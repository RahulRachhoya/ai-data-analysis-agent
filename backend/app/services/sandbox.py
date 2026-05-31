import base64
import io
import os
from typing import Any

from app.config import E2B_API_KEY


class SandboxService:
    """Service wrapping E2B code interpreter sandbox for secure Python execution."""

    def __init__(self):
        self._sandbox = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def start(self):
        """Create a new E2B sandbox session."""
        from e2b_code_interpreter import Sandbox

        self._sandbox = Sandbox(api_key=E2B_API_KEY)
        # Pre-install common data science packages
        self._sandbox.commands.run(
            "pip install pandas numpy matplotlib seaborn plotly scipy scikit-learn -q"
        )
        return self

    async def upload_file(self, local_path: str, sandbox_path: str):
        """Upload a file to the sandbox."""
        if not self._sandbox:
            raise RuntimeError("Sandbox not started")
        with open(local_path, "rb") as f:
            self._sandbox.files.write(sandbox_path, f.read())

    async def run_code(self, code: str) -> dict[str, Any]:
        """Run Python code in the sandbox and return results."""
        if not self._sandbox:
            raise RuntimeError("Sandbox not started")

        execution = self._sandbox.run_code(code)

        result = {
            "text": execution.text,
            "stdout": execution.logs.stdout if execution.logs else [],
            "stderr": execution.logs.stderr if execution.logs else [],
            "error": None,
            "plots": [],
            "plotly_figures": [],
        }

        if execution.error:
            result["error"] = {
                "name": execution.error.name,
                "value": execution.error.value,
                "traceback": execution.error.traceback,
            }
            return result

        # Extract matplotlib/seaborn plots from results
        for item in (execution.results or []):
            if hasattr(item, "png") and item.png:
                img_b64 = base64.b64encode(item.png).decode("utf-8")
                result["plots"].append({
                    "type": "matplotlib",
                    "image": f"data:image/png;base64,{img_b64}",
                })

            # Check for Plotly figures (saved as HTML or JSON)
            if hasattr(item, "data") and item.data:
                result["plotly_figures"].append(item.data)

        return result

    async def read_file(self, path: str) -> bytes:
        """Read a file from the sandbox."""
        if not self._sandbox:
            raise RuntimeError("Sandbox not started")
        return self._sandbox.files.read(path)

    async def close(self):
        """Close the sandbox session."""
        if self._sandbox:
            try:
                self._sandbox.close()
            except Exception:
                pass
            self._sandbox = None


def get_sandbox_service() -> SandboxService:
    """Factory for creating sandbox services."""
    return SandboxService()
