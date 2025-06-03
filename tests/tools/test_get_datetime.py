from datetime import datetime

import pytest

from llmbrix.tools import GetDatetime


def test_get_datetime_exec_output_format():
    tool = GetDatetime()
    tool_output = tool.exec().content
    parsed = datetime.strptime(tool_output, "%Y-%m-%d %H:%M:%S")
    assert isinstance(parsed, datetime)


def test_get_datetime_custom_format():
    fmt = "%d/%m/%Y"
    tool = GetDatetime(datetime_fmt=fmt)
    tool_output = tool.exec().content
    parsed = datetime.strptime(tool_output, fmt)
    assert isinstance(parsed, datetime)


def test_get_datetime_invalid_desc_format():
    with pytest.raises(ValueError):
        GetDatetime(tool_desc="This description lacks datetime format placeholder")
