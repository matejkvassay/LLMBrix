from typing import List, Optional

from openai.types.chat import ChatCompletionMessageToolCall

from llmbrix.msg.msg import Msg


class AssistantMsg(Msg):
    content: Optional[str] = None
    role: str = "assistant"
    tool_calls: Optional[List[ChatCompletionMessageToolCall]] = None

    def __str__(self):
        basic_info = super().__str__()
        tool_names = ""
        if self.tool_calls:
            tool_names = ", ".join(t.function.name for t in self.tool_calls)
        return f"{basic_info} | tool calls: [{tool_names}]"
