from llmbrix.msg.msg import Msg


class ToolOutputMsg(Msg):
    call_id: str
    output: str
    type: str = "function_call_output"
