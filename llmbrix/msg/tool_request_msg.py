from openai.types.responses import ResponseFunctionToolCall

from llmbrix.msg.msg import Msg


class ToolRequestMsg(Msg):
    call_id: str
    name: str
    arguments: str
    type: str = "function_call"

    @classmethod
    def from_openai(cls, tool_call: ResponseFunctionToolCall):
        return cls(call_id=tool_call.call_id, name=tool_call.name, arguments=tool_call.arguments)
