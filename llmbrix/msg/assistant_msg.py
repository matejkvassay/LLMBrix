from typing import List, Optional

from openai.types.chat import ChatCompletionMessageToolCall
from openai.types.chat.chat_completion import Choice

from llmbrix.base.msg_base import MsgBase


class AssistantMsg(MsgBase):
    content: Optional[str] = None
    role: str = "assistant"
    tool_calls: Optional[List[ChatCompletionMessageToolCall]] = None

    @classmethod
    def from_choice(cls, choice: Choice):
        return cls(content=choice.message.content, tool_calls=choice.message.tool_calls)

    def __str__(self):
        if self.tool_calls is None:
            return super().__str__()
        tool_names = ", ".join([t.function.name for t in self.tool_calls])
        content = self.content if self.content is not None else "<no content>"
        return f'{self.role.upper()}: "{content}" : tool_calls=[{tool_names}]'
