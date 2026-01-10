from unittest.mock import MagicMock, patch

import PIL.Image
import pytest
from google.genai import types

from llmbrix.msg import ModelMsg, ToolMsg, UserMsg
from llmbrix.tool_agent import ToolAgent


@pytest.fixture
def gemini_model_mock():
    return MagicMock()


@pytest.fixture
def tool_agent(gemini_model_mock):
    from llmbrix.tool_calling import BaseTool

    mock_tool = MagicMock(spec=BaseTool)
    return ToolAgent(
        gemini_model=gemini_model_mock,
        system_instruction="You are a helpful assistant",
        tools=[mock_tool],
        loop_limit=3,
    )


def test_initialization_invalid_loop_limit(gemini_model_mock):
    with pytest.raises(ValueError, match="Loop limit must be greater than 0"):
        ToolAgent(gemini_model=gemini_model_mock, system_instruction="test", loop_limit=0)


def test_chat_iter_invalid_input_combination(tool_agent):
    user_msg = UserMsg(text="Hello")
    with pytest.raises(ValueError, match="Cannot combine multimodal inputs"):
        next(tool_agent.chat_iter(user_input=user_msg, images=[MagicMock(spec=PIL.Image.Image)]))


def test_chat_runtime_error_no_model_msg(tool_agent):
    with patch.object(tool_agent, "chat_iter") as mock_iter:
        mock_iter.return_value = iter([UserMsg(text="hi")])
        with pytest.raises(RuntimeError, match="Agent failed to produce a ModelMsg"):
            tool_agent.chat("hi")


def test_hallucinated_tool_calls_at_loop_limit(gemini_model_mock, tool_agent):
    tool_agent.loop_limit = 1
    call_part = types.Part(function_call=types.FunctionCall(name="test_tool", args={}))
    hallucinated_msg = ModelMsg(parts=[call_part])
    gemini_model_mock.generate.return_value = hallucinated_msg

    gen = tool_agent.chat_iter("run tool")
    next(gen)
    next(gen)
    with pytest.raises(ValueError, match="Model hallucinated tool calls"):
        next(gen)


def test_successful_chat_history_update(gemini_model_mock):
    mock_history = MagicMock()
    mock_history.get.return_value = []
    agent = ToolAgent(gemini_model=gemini_model_mock, system_instruction="test", chat_history=mock_history)

    response_msg = ModelMsg.from_text("Hello there")
    gemini_model_mock.generate.return_value = response_msg

    agent.chat("Hi")

    assert mock_history.insert_batch.called
    inserted_msgs = mock_history.insert_batch.call_args[0][0]
    assert len(inserted_msgs) == 2
    assert isinstance(inserted_msgs[0], UserMsg)
    assert isinstance(inserted_msgs[1], ModelMsg)


def test_tool_execution_loop(gemini_model_mock):
    mock_tool = MagicMock()
    agent = ToolAgent(gemini_model=gemini_model_mock, system_instruction="test", tools=[mock_tool], loop_limit=2)

    call_obj = types.FunctionCall(name="get_weather", args={"loc": "NY"})
    call_part = types.Part(function_call=call_obj)
    msg_with_tool = ModelMsg(parts=[call_part])
    final_msg = ModelMsg.from_text("It is sunny")
    tool_res = ToolMsg(tool_call=call_obj, result={"temp": "25C"})

    gemini_model_mock.generate.side_effect = [msg_with_tool, final_msg]

    with patch.object(agent.tool_executor, "execute_iter") as mock_exec:
        mock_exec.return_value = iter([tool_res])
        results = list(agent.chat_iter("What is the weather?"))

        assert len(results) == 4
        assert isinstance(results[0], UserMsg)
        assert results[1] == msg_with_tool
        assert isinstance(results[2], ToolMsg)
        assert results[3] == final_msg
        assert gemini_model_mock.generate.call_count == 2


def test_chat_returns_final_model_msg(gemini_model_mock):
    agent = ToolAgent(gemini_model=gemini_model_mock, system_instruction="test")
    expected_msg = ModelMsg.from_text("Final Answer")
    gemini_model_mock.generate.return_value = expected_msg

    result = agent.chat("Hello")
    assert result == expected_msg
