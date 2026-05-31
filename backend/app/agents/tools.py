import json
from typing import Any

from langchain_core.tools import tool


@tool
def analyze_dataframe_schema(dataset_info: str) -> str:
    """Analyze the schema and preview of a dataset.
    
    Args:
        dataset_info: JSON string with columns, dtypes, row_count, preview rows, and numeric_stats
    """
    info = json.loads(dataset_info)
    cols = info.get("columns", [])
    dtypes = info.get("dtypes", {})
    preview = info.get("preview", [])
    stats = info.get("numeric_stats", {})
    row_count = info.get("row_count", 0)

    schema_lines = [f"Dataset has {row_count} rows and {len(cols)} columns.\n"]
    schema_lines.append("Columns:")
    for col in cols:
        dtype = dtypes.get(col, "unknown")
        schema_lines.append(f"  - {col} ({dtype})")

    if stats:
        schema_lines.append("\nNumeric columns summary:")
        for col, s in stats.items():
            schema_lines.append(
                f"  - {col}: min={s['min']}, max={s['max']}, mean={s['mean']:.2f}, median={s['median']:.2f}"
                if s["mean"] is not None
                else f"  - {col}: (no numeric data)"
            )

    schema_lines.append(f"\nPreview (first {len(preview)} rows):")
    for i, row in enumerate(preview):
        schema_lines.append(f"  Row {i + 1}: {json.dumps(row)}")

    return "\n".join(schema_lines)


@tool
def check_code_result(evaluation_input: str) -> str:
    """Check whether code execution results answer the user's question.
    
    Args:
        evaluation_input: JSON string with 'question', 'stdout', 'stderr', 'has_error', and 'text'
    """
    data = json.loads(evaluation_input)
    question = data.get("question", "")
    stdout = data.get("stdout", "")
    stderr = data.get("stderr", "")
    has_error = data.get("has_error", False)
    text = data.get("text", "")

    result_lines = [
        f"Question: {question}",
        f"Has error: {has_error}",
        f"Stdout length: {len(stdout)} chars",
        f"Output text: {text[:500] if text else '(none)'}",
    ]

    if stderr:
        result_lines.append(f"Stderr: {stderr[:500]}")

    return "\n".join(result_lines)


tools = [analyze_dataframe_schema, check_code_result]
