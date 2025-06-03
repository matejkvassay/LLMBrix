from llmbrix.msg.msg import Msg


class ToolOutputMsg(Msg):
    """
    Message containing output from tool execution.
    """

    call_id: str  # used to pair this message with relevant ToolRequestMsg
    output: str  # contains str output from tool call
    type: str = "function_call_output"
