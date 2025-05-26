from llmbrix.conv_hist import ConvTurnHist
from llmbrix.msg import AssistantMsg, SystemMsg, ToolMsg, UserMsg


def test_conv_turn_hist():
    hist = ConvTurnHist(max_turns=3, system_msg=SystemMsg("sys_msg"))
    assert len(hist) == 0
    assert hist.get() == [SystemMsg("sys_msg")]

    hist.add(UserMsg("hey"))
    hist.add(AssistantMsg("hehe"))
    hist.add(ToolMsg(content="tool_response", tool_call_id="id1"))

    assert len(hist) == 1
    assert hist.get() == [
        SystemMsg("sys_msg"),
        UserMsg("hey"),
        AssistantMsg("hehe"),
        ToolMsg(content="tool_response", tool_call_id="id1"),
    ]

    hist.add(UserMsg("hey2"))
    hist.add(AssistantMsg("hehe2"))

    assert len(hist) == 2

    hist.add(UserMsg("hey"))
    hist.add(AssistantMsg("hehe3"))
    hist.add(ToolMsg(content="tool_response", tool_call_id="id1"))
    hist.add(AssistantMsg(None))
    hist.add(ToolMsg(content="tool_response", tool_call_id="id1"))
    hist.add(ToolMsg(content="tool_response", tool_call_id="id1"))
    hist.add(AssistantMsg("resp"))

    assert len(hist) == 3

    hist.add(UserMsg("hey4"))
    hist.add(AssistantMsg("hehe4"))
    assert len(hist) == 3

    assert hist.get()[0] == SystemMsg("sys_msg")
    assert hist.get()[1] == UserMsg("hey2")
    assert hist.get()[-1] == AssistantMsg("hehe4")
