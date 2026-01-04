import pytest
from google.genai import types

from llmbrix.chat_history import ChatHistory
from llmbrix.msg import ModelMsg, ToolMsg, UserMsg


def create_user_msg(text="hi"):
    return UserMsg(text=text)


def create_model_msg(text="hello"):
    return ModelMsg.from_text(text=text)


def create_tool_msg(name="get_weather", result="sunny"):
    """Helper to create a ToolMsg with a mock function call."""
    call = types.FunctionCall(name=name, args={})
    return ToolMsg(tool_call=call, result={"result": result})


def test_history_initialization():
    history = ChatHistory(max_turns=3)
    assert history.count_conversation_turns() == 0
    assert len(history) == 0


def test_error_on_leading_model_msg():
    history = ChatHistory()
    with pytest.raises(ValueError):
        history.insert(create_model_msg())


def test_error_on_leading_tool_msg():
    history = ChatHistory()
    with pytest.raises(ValueError):
        history.insert(create_tool_msg())


def test_single_turn_with_tool_logic():
    history = ChatHistory()
    history.insert(create_user_msg())
    history.insert(create_model_msg("Calling tool..."))
    history.insert(create_tool_msg())
    history.insert(create_model_msg("Here is the info."))
    assert history.count_conversation_turns() == 1
    assert len(history) == 4


def test_max_turns_truncation_on_batch():
    history = ChatHistory(max_turns=1)
    msgs = [create_user_msg("U1"), create_model_msg("M1"), create_user_msg("U2"), create_model_msg("M2")]
    history.insert_batch(msgs)

    assert history.count_conversation_turns() == 1
    assert history.get()[0].parts[0].text == "U2"


def test_pop_on_empty_history():
    history = ChatHistory()
    assert history.pop() == []


def test_get_n_clamping():
    history = ChatHistory()
    history.insert(create_user_msg("U1"))
    assert history.get(n=0) == []
    assert history.get(n=-10) == []


def test_invalid_type_error_message():
    history = ChatHistory()
    with pytest.raises(TypeError):
        history.insert(123)


def test_turn_len_consistency():
    history = ChatHistory()
    history.insert(create_user_msg())
    history.insert(create_model_msg())
    history.insert(create_tool_msg())

    assert len(history) == len(history.get())


def test_multiple_model_responses_in_turn():
    history = ChatHistory()
    history.insert(create_user_msg())
    history.insert(create_model_msg("Part 1"))
    history.insert(create_model_msg("Part 2"))

    assert history.count_conversation_turns() == 1
    assert len(history) == 3
