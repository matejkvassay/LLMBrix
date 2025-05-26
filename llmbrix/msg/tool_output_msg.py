from typing_extensions import override

from llmbrix.msg.msg import Msg


class ToolOutputMsg(Msg):
    call_id: str
    content: str

    role: str = "tool_output"
    type: str = "function_call_output"

    @override
    def to_openai(self, exclude_extra: list[str] = None) -> dict:
        if not exclude_extra:
            exclude_extra = []
        exclude_extra.append("role")
        return super().to_openai(exclude_extra=exclude_extra)

    def __str__(self):
        basic_info = super().__str__()
        return f"{basic_info} | tools call ID: {self.call_id}"
