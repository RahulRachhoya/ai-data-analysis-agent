import json
from typing import Any


def convert_matplotlib_to_html(img_data_url: str, alt_text: str = "Chart") -> str:
    """Wrap a matplotlib PNG data URL in an HTML img tag."""
    return f'<img src="{img_data_url}" alt="{alt_text}" style="max-width:100%;height:auto;border-radius:8px;" />'


def serialize_plotly_figure(figure_json: dict) -> dict:
    """Serialize a Plotly figure dict for safe JSON transport."""
    return json.loads(json.dumps(figure_json, default=str))


def format_results_for_response(execution_result: dict[str, Any]) -> dict[str, Any]:
    """Format the full execution result into a frontend-friendly response."""
    formatted = {
        "stdout": "\n".join(execution_result.get("stdout", [])),
        "stderr": "\n".join(execution_result.get("stderr", [])),
        "plots": execution_result.get("plots", []),
        "plotly_figures": [],
        "text": execution_result.get("text", ""),
        "error": execution_result.get("error"),
    }

    for fig in execution_result.get("plotly_figures", []):
        if isinstance(fig, dict):
            formatted["plotly_figures"].append(serialize_plotly_figure(fig))

    return formatted
