from openai.types.responses import ResponseFunctionToolCall

from llmbrix.msg.msg import Msg


class ToolRequestMsg(Msg):
    """
    Message containing tool call request form LLM.
    """

    call_id: str  # Used to pair this request with ToolOutputMsg
    name: str  # Name of tool to be executed
    arguments: str  # Parameters to be passed into the tool in JSON str format
    type: str = "function_call"

    @classmethod
    def from_openai(cls, tool_call: ResponseFunctionToolCall):
        """
        Transform OpenAI tool call object from LLM output list to ToolRequestMsg.

        :param tool_call: ResponseFunctionToolCall instance
        :return: ToolRequestMsg instance
        """
        return cls(call_id=tool_call.call_id, name=tool_call.name, arguments=tool_call.arguments)
