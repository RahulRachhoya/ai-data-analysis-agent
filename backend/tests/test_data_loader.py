"""Tests for app.services.data_loader — NaN handling, None string preservation,
CSV and JSON upload, and JSON-safe serialization."""

import json

import pytest

from app.services.data_loader import (
    _make_json_safe,
    _NA_VALUES,
    load_from_file,
    get_dataset_info,
)


class TestMakeJsonSafe:
    """Verify _make_json_safe correctly converts non-serializable types."""

    def test_nan_becomes_none(self):
        import math
        assert _make_json_safe(float("nan")) is None
        assert _make_json_safe(float("inf")) is None
        assert _make_json_safe(float("-inf")) is None

    def test_none_stays_none(self):
        assert _make_json_safe(None) is None

    def test_numpy_int_converts(self):
        import numpy as np
        assert _make_json_safe(np.int64(42)) == 42
        assert isinstance(_make_json_safe(np.int64(42)), int)

    def test_numpy_float_converts(self):
        import numpy as np
        result = _make_json_safe(np.float64(3.14))
        assert result == 3.14
        assert isinstance(result, float)

    def test_numpy_float_nan(self):
        import numpy as np
        assert _make_json_safe(np.float64("nan")) is None

    def test_numpy_bool_converts(self):
        import numpy as np
        assert _make_json_safe(np.bool_(True)) is True
        assert _make_json_safe(np.bool_(False)) is False

    def test_regular_float_preserved(self):
        assert _make_json_safe(3.14) == 3.14

    def test_regular_int_preserved(self):
        assert _make_json_safe(42) == 42

    def test_string_preserved(self):
        assert _make_json_safe("None") == "None"
        assert _make_json_safe("hello") == "hello"

    def test_pandas_timestamp(self):
        import pandas as pd
        ts = pd.Timestamp("2024-01-01")
        assert isinstance(_make_json_safe(ts), str)
        assert "2024" in str(_make_json_safe(ts))

    def test_dict_recursive(self):
        val = {"a": float("nan"), "b": {"c": None}}
        result = _make_json_safe(val)
        assert result["a"] is None
        assert result["b"]["c"] is None

    def test_list_recursive(self):
        val = [float("nan"), "hello", None]
        result = _make_json_safe(val)
        assert result[0] is None
        assert result[1] == "hello"
        assert result[2] is None


class TestNAValues:
    """Verify the _NA_VALUES list excludes 'None' but includes standard NA markers."""

    def test_none_is_not_na(self):
        assert "None" not in _NA_VALUES

    def test_empty_string_is_na(self):
        assert "" in _NA_VALUES

    def test_nan_is_na(self):
        assert "NaN" in _NA_VALUES

    def test_null_is_na(self):
        assert "null" in _NA_VALUES

    def test_na_is_na(self):
        assert "NA" in _NA_VALUES


class TestLoadFromFile:
    """Integration tests for load_from_file with actual CSV and JSON data."""

    CSV_WITH_NONE = b"name,status,score\nAlice,Active,10\nBob,None,20\nCharlie,Inactive,\n"
    CSV_WITH_EMPTY = b"a,b,c\n1,,3\n4,5,\n,7,9\n"

    def test_csv_none_string_preserved(self):
        result = load_from_file(self.CSV_WITH_NONE, "test.csv")
        assert result["row_count"] == 3
        preview = result["preview"]
        # "None" string should NOT be converted to null
        assert preview[1]["status"] == "None"
        # Empty cell should be None/null
        assert preview[2]["score"] is None

    def test_csv_empty_cells_become_null(self):
        result = load_from_file(self.CSV_WITH_EMPTY, "test.csv")
        preview = result["preview"]
        assert preview[0]["b"] is None  # empty -> null
        assert preview[1]["c"] is None  # empty -> null
        assert preview[2]["a"] is None  # empty -> null

    def test_json_with_nulls(self):
        data = json.dumps([
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": None},
        ]).encode()
        result = load_from_file(data, "test.json")
        assert result["row_count"] == 2
        preview = result["preview"]
        assert preview[0]["age"] == 30.0
        assert preview[1]["age"] is None

    def test_json_serializable_output(self):
        """The entire response dict must be JSON-serializable (no NaN values)."""
        data = json.dumps([
            {"x": 1, "y": None},
            {"x": 2, "y": "text"},
        ]).encode()
        result = load_from_file(data, "test.json")
        dumped = json.dumps(result, allow_nan=False)
        assert '"y": null' in dumped

    def test_unsupported_format_raises(self):
        with pytest.raises(ValueError, match="Unsupported file format"):
            load_from_file(b"some data", "test.txt")


class TestGetDatasetInfo:
    """Test that get_dataset_info returns proper metadata."""

    def test_returns_none_for_unknown_id(self):
        info = get_dataset_info("nonexistent-id")
        assert info is None
