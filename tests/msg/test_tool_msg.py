import pytest
from google.genai import types

from llmbrix.msg.model_msg import ModelMsg
from llmbrix.msg.tool_msg import ToolMsg


def test_tool_msg_name_matching():
    call = types.FunctionCall(name="get_weather", args={"city": "Berlin"})
    msg = ToolMsg(tool_call=call, result={"temp": 20})
    assert msg.parts[0].function_response.name == "get_weather"


def test_tool_msg_handles_null_result():
    call = types.FunctionCall(name="delete_file", args={"id": "123"})
    msg = ToolMsg(tool_call=call, result=None)
    # None is not a dict, so it should be wrapped
    assert msg.parts[0].function_response.response == {"result": None}


def test_tool_msg_batch_ordering():
    """Verify that results are mapped to calls in the correct order."""
    parts = [
        types.Part(function_call=types.FunctionCall(name="first", args={})),
        types.Part(function_call=types.FunctionCall(name="second", args={})),
    ]
    model_msg = ModelMsg(parts=parts)
    results = ["A", "B"]

    tool_msgs = ToolMsg.from_results(model_msg, results)
    assert tool_msgs[0].parts[0].function_response.name == "first"
    assert tool_msgs[0].parts[0].function_response.response == {"result": "A"}
    assert tool_msgs[1].parts[0].function_response.name == "second"
    assert tool_msgs[1].parts[0].function_response.response == {"result": "B"}


def test_tool_msg_batch_mismatch_raises():
    model_msg = ModelMsg(parts=[types.Part(function_call=types.FunctionCall(name="a", args={}))])
    with pytest.raises(ValueError, match="Count mismatch"):
        ToolMsg.from_results(model_msg, results=[])  # 1 call, 0 results
