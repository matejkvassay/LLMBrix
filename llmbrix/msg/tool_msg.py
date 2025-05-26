from llmbrix.msg.msg import Msg


class ToolMsg(Msg):
    content: str
    tool_call_id: str
    role: str = "tools"

    def __str__(self):
        basic_info = super().__str__()
        return f"{basic_info} | tools call ID: {self.tool_call_id}"
