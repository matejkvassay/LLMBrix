from openai.types.responses import ResponseFunctionToolCall
from typing_extensions import override

from llmbrix.msg.msg import Msg


class ToolRequestMsg(Msg):
    call_id: str
    name: str
    arguments: str

    content: None = None
    role: str = "tool_request"
    type: str = "function_call"

    @classmethod
    def from_openai(cls, tool_call: ResponseFunctionToolCall):
        return cls(call_id=tool_call.call_id, name=tool_call.name, arguments=tool_call.arguments)

    @override
    def to_openai(self, exclude_extra: list[str] = None) -> dict:
        if not exclude_extra:
            exclude_extra = []
        exclude_extra += ["role", "content"]
        return super().to_openai(exclude_extra=exclude_extra)

    def __str__(self):
        basic_info = super().__str__()
        return (
            f"{basic_info} | tools call ID: {self.call_id} "
            f"| tool name: {self.call_id} | tool args: {self.arguments}"
        )
