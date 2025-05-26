from llmbrix.msg.msg import Msg


class ToolMsg(Msg):
    content: str
    tool_call_id: str
    role: str = "tool"

    def __str__(self):
        basic_info = super().__str__()
        return f"{basic_info} | tool call ID: {self.tool_call_id}"
