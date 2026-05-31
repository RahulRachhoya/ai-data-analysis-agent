import json
import math
import uuid
import os
from io import BytesIO, StringIO

import pandas as pd
import numpy as np
import httpx
from typing import Any
from app.config import DATASETS_DIR


def _make_json_safe(val: Any) -> Any:
    """Recursively convert values to JSON-safe equivalents."""
    if val is None:
        return None
    if isinstance(val, (pd.Timestamp, pd.Period, pd.Timedelta)):
        return str(val)
    if isinstance(val, np.integer):
        return int(val)
    if isinstance(val, (np.floating, float)):
        if math.isnan(val) or math.isinf(val):
            return None
        return float(val)
    if isinstance(val, np.bool_):
        return bool(val)
    if isinstance(val, dict):
        return {k: _make_json_safe(v) for k, v in val.items()}
    if isinstance(val, list):
        return [_make_json_safe(v) for v in val]
    if isinstance(val, tuple):
        return [_make_json_safe(v) for v in val]
    if isinstance(val, bytes):
        return val.decode("utf-8", errors="replace")
    # pandas NA / NaT
    try:
        if pd.isna(val):
            return None
    except (TypeError, ValueError):
        pass
    return val


# Default NA values from pandas, EXCLUDING "None" (which is a valid string value)
_NA_VALUES = [
    "",
    "#N/A",
    "#N/A N/A",
    "#NA",
    "-1.#IND",
    "-1.#QNAN",
    "-NaN",
    "-nan",
    "1.#IND",
    "1.#QNAN",
    "N/A",
    "NA",
    "NULL",
    "NaN",
    "n/a",
    "nan",
    "null",
]


def _save_dataset(df: pd.DataFrame, filename: str) -> str:
    """Save a DataFrame to disk and return a dataset_id."""
    dataset_id = str(uuid.uuid4())
    ext = os.path.splitext(filename)[1].lower()
    save_path = os.path.join(DATASETS_DIR, f"{dataset_id}{ext}")

    if ext == ".json":
        df.to_json(save_path, orient="records", date_format="iso")
    else:
        df.to_csv(save_path, index=False)

    return dataset_id


def _build_response(dataset_id: str, filename: str, df: pd.DataFrame) -> dict:
    """Build a standard response dict from a DataFrame."""
    columns = list(df.columns)
    dtypes = {col: str(df[col].dtype) for col in columns}
    preview_rows = min(5, len(df))
    preview = df.head(preview_rows).to_dict(orient="records")

    # Convert non-serializable types (NaN, NaT, numpy types, etc.)
    for row in preview:
        for k, v in row.items():
            row[k] = _make_json_safe(v)

    # Stats for numeric columns
    numeric_stats = {}
    for col in df.select_dtypes(include=["number"]).columns:
        numeric_stats[col] = {
            "min": float(df[col].min()) if pd.notna(df[col].min()) else None,
            "max": float(df[col].max()) if pd.notna(df[col].max()) else None,
            "mean": float(df[col].mean()) if pd.notna(df[col].mean()) else None,
            "median": float(df[col].median()) if pd.notna(df[col].median()) else None,
        }

    return {
        "dataset_id": dataset_id,
        "filename": filename,
        "row_count": len(df),
        "columns": columns,
        "dtypes": dtypes,
        "preview": preview,
        "numeric_stats": numeric_stats,
        "file_path": os.path.join(DATASETS_DIR, f"{dataset_id}{os.path.splitext(filename)[1]}"),
    }


def load_from_file(content: bytes, filename: str) -> dict:
    """Load a dataset from uploaded file bytes."""
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".json":
        data = json.loads(content)
        df = pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame([data])
    elif ext == ".csv":
        df = pd.read_csv(BytesIO(content), keep_default_na=False, na_values=_NA_VALUES)
    else:
        raise ValueError(f"Unsupported file format: {ext}. Please upload CSV or JSON.")

    dataset_id = _save_dataset(df, filename)
    return _build_response(dataset_id, filename, df)


def load_from_url(url: str) -> dict:
    """Load a dataset from a public URL."""
    response = httpx.get(url, follow_redirects=True, timeout=30)
    response.raise_for_status()

    filename = url.split("/")[-1].split("?")[0] or "remote_data"
    content_type = response.headers.get("content-type", "")

    if "json" in content_type or filename.endswith(".json"):
        data = response.json()
        df = pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame([data])
        filename = filename if filename.endswith(".json") else "remote_data.json"
    else:
        df = pd.read_csv(StringIO(response.text), keep_default_na=False, na_values=_NA_VALUES)
        filename = filename if filename.endswith(".csv") else "remote_data.csv"

    dataset_id = _save_dataset(df, filename)
    return _build_response(dataset_id, filename, df)


def load_from_api(
    url: str,
    method: str = "GET",
    headers: dict | None = None,
    body: dict | None = None,
    response_path: str | None = None,
) -> dict:
    """Load a dataset from an API endpoint."""
    with httpx.Client(timeout=30) as client:
        if method.upper() == "POST":
            resp = client.post(url, headers=headers, json=body)
        else:
            resp = client.get(url, headers=headers)
        resp.raise_for_status()

    raw_data = resp.json()

    # Navigate nested JSON if a path is provided
    if response_path:
        for key in response_path.split("."):
            if isinstance(raw_data, dict):
                raw_data = raw_data[key]
            else:
                raise ValueError(f"Cannot navigate path '{response_path}': reached non-dict value")

    df = pd.DataFrame(raw_data) if isinstance(raw_data, list) else pd.DataFrame([raw_data])

    filename = "api_data.csv"
    dataset_id = _save_dataset(df, filename)
    return _build_response(dataset_id, filename, df)


def get_dataset_info(dataset_id: str) -> dict | None:
    """Get metadata about a loaded dataset by ID."""
    for f in os.listdir(DATASETS_DIR):
        if f.startswith(dataset_id):
            file_path = os.path.join(DATASETS_DIR, f)
            ext = os.path.splitext(f)[1].lower()
            if ext == ".json":
                df = pd.read_json(file_path)
            else:
                df = pd.read_csv(file_path, keep_default_na=False, na_values=_NA_VALUES)

            dtypes = {col: str(df[col].dtype) for col in df.columns}
            columns = list(df.columns)
            row_count = len(df)

            # Build preview
            preview_rows = min(5, row_count)
            preview = df.head(preview_rows).to_dict(orient="records")
            for row in preview:
                for k, v in row.items():
                    row[k] = _make_json_safe(v)

            # Build numeric stats
            numeric_stats = {}
            for col in df.select_dtypes(include=["number"]).columns:
                numeric_stats[col] = {
                    "min": float(df[col].min()) if pd.notna(df[col].min()) else None,
                    "max": float(df[col].max()) if pd.notna(df[col].max()) else None,
                    "mean": float(df[col].mean()) if pd.notna(df[col].mean()) else None,
                    "median": float(df[col].median()) if pd.notna(df[col].median()) else None,
                }

            return {
                "file_path": file_path,
                "columns": columns,
                "dtypes": dtypes,
                "row_count": row_count,
                "preview": preview,
                "numeric_stats": numeric_stats,
            }
    return None
