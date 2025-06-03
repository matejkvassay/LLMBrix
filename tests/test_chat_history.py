import pytest

from llmbrix.chat_history import ChatHistory
from llmbrix.msg import AssistantMsg, SystemMsg, ToolOutputMsg, UserMsg


@pytest.fixture
def user_msg():
    return UserMsg(role="user", content="Hello!")


@pytest.fixture
def assistant_msg():
    return AssistantMsg(role="assistant", content="Hi, how can I help?")


@pytest.fixture
def tool_msg():
    return ToolOutputMsg(output="Tool output", call_id="xyz")


@pytest.fixture
def system_msg():
    return SystemMsg(role="system", content="You are a helpful assistant.")


def test_add_valid_sequence(user_msg, assistant_msg, system_msg):
    history = ChatHistory()
    history.add(system_msg)
    history.add(user_msg)
    history.add(assistant_msg)

    messages = history.get()

    assert messages[0] == system_msg
    assert messages[1] == user_msg
    assert messages[2] == assistant_msg
    assert len(history) == 3
    assert history.count_conv_turns() == 1


def test_add_tool_message_after_user(user_msg, tool_msg):
    history = ChatHistory()
    history.add(user_msg)
    history.add(tool_msg)

    messages = history.get()
    assert messages[0] == user_msg
    assert messages[1] == tool_msg
    assert len(history) == 2
    assert history.count_conv_turns() == 1


def test_reject_assistant_before_user(assistant_msg):
    history = ChatHistory()
    with pytest.raises(ValueError, match="Conversation must start with a UserMsg."):
        history.add(assistant_msg)


def test_reject_tool_before_user(tool_msg):
    history = ChatHistory()
    with pytest.raises(ValueError, match="Conversation must start with a UserMsg."):
        history.add(tool_msg)


def test_add_many_mixed_messages(user_msg, assistant_msg, system_msg):
    history = ChatHistory()
    history.add_many([system_msg, user_msg, assistant_msg])
    messages = history.get()

    assert len(messages) == 3
    assert messages[0] == system_msg
    assert messages[1] == user_msg
    assert messages[2] == assistant_msg


def test_get_returns_last_n_turns(user_msg, assistant_msg):
    history = ChatHistory(max_turns=10)

    # Add 3 user-assistant turns
    for i in range(3):
        history.add(UserMsg(role="user", content=f"Q{i}"))
        history.add(AssistantMsg(role="assistant", content=f"A{i}"))

    all_msgs = history.get()
    last_turn = history.get(n=1)
    last_two_turns = history.get(n=2)

    assert len(all_msgs) == 1 + 3 * 2 or len(all_msgs) == 3 * 2  # with or without system msg
    assert last_turn[-2].content == "Q2"
    assert last_turn[-1].content == "A2"
    assert last_two_turns[-4].content == "Q1"
    assert last_two_turns[-3].content == "A1"


def test_trim_behavior(user_msg):
    history = ChatHistory(max_turns=2)

    # Add 3 full turns
    for i in range(3):
        history.add(UserMsg(role="user", content=f"Turn {i}"))
        history.add(AssistantMsg(role="assistant", content=f"Reply {i}"))

    assert len(history) == 4
    assert history.count_conv_turns() == 2  # only 2 most recent turns retained

    msgs = history.get()
    assert "Turn 0" not in [m.content for m in msgs]


def test_system_msg_optional(user_msg, assistant_msg):
    history = ChatHistory()
    history.add(user_msg)
    history.add(assistant_msg)

    msgs = history.get()
    assert msgs[0] == user_msg
    assert len(msgs) == 2


def test_multiple_system_msg_replacement(user_msg, system_msg):
    history = ChatHistory()
    history.add(SystemMsg(role="system", content="First"))
    history.add(SystemMsg(role="system", content="Replaced"))
    history.add(user_msg)

    msgs = history.get()
    assert msgs[0].content == "Replaced"
