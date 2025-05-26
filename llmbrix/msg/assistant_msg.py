from typing import List, Optional

from openai.types.chat import ChatCompletionMessageToolCall

from llmbrix.msg.msg import Msg


class AssistantMsg(Msg):
    content: Optional[str] = None
    role: str = "assistant"
    tool_calls: Optional[List[ChatCompletionMessageToolCall]] = None

    def __str__(self):
        if self.tool_calls is None:
            return super().__str__()
        tool_names = ", ".join([t.function.name for t in self.tool_calls])
        content = self.content if self.content is not None else "<no content>"
        return f'{self.role.upper()}: "{content}" : tool_calls=[{tool_names}]'
