from llmbrix.msg.msg import Msg


class ToolMsg(Msg):
    content: str
    tool_call_id: str
    role: str = "tool"

    def __str__(self):
        content = self.content if self.content is not None else "<no tool output>"
        return f'{self.role.upper()}:{self.tool_call_id}: "{content}"'
