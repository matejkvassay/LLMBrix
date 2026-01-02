from datetime import datetime
from unittest.mock import patch

import pytest

from propus.tools import DatetimeTool


@pytest.fixture
def datetime_tool():
    return DatetimeTool()


def test_structure_of_output(datetime_tool):
    """Verify all expected keys exist and success is True."""
    result = datetime_tool.execute()

    assert result.success is True
    assert "year" in result.result
    assert "month" in result.result
    assert "weekday" in result.result
    assert "iso_format" in result.result
    assert result.debug_trace["engine"] == "python_datetime_module"


def test_mocked_fixed_time(datetime_tool):
    """Verify that the tool correctly extracts parts of the date from a fixed point in time."""
    # We mock datetime.now to return a specific 'frozen' time
    frozen_now = datetime(2026, 1, 2, 10, 0, 0)  # Friday

    with patch("propus.tools.datetime_tool.datetime") as mock_datetime:
        mock_datetime.now.return_value = frozen_now
        # Important: handle the strftime call if necessary,
        # but usually mocking .now() is enough if the tool calls datetime.now()

        output = datetime_tool.execute()
        res = output.result

        assert res["year"] == 2026
        assert res["month"] == 1
        assert res["day"] == 2
        assert res["hour"] == 10
        assert res["weekday"] == "Friday"
        assert "2026-01-02T10:00:00" in res["iso_format"]


def test_iso_format_validity(datetime_tool):
    """Ensure the iso_format string is actually valid and can be parsed back."""
    result = datetime_tool.execute()
    iso_str = result.result["iso_format"]

    # If this doesn't raise an error, the format is correct
    parsed = datetime.fromisoformat(iso_str)
    assert parsed.year == result.result["year"]


def test_weekday_logic(datetime_tool):
    """Quick check that weekday is a full string like 'Monday', not an int."""
    result = datetime_tool.execute()
    assert isinstance(result.result["weekday"], str)
    # Check if it's one of the 7 days
    days = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}
    assert result.result["weekday"] in days
