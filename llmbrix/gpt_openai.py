import logging

from openai import OpenAI
from openai.types.chat.chat_completion import Choice

from llmbrix.msg import AssistantMsg, Msg
from llmbrix.tool import Tool

logger = logging.getLogger(__name__)
client = OpenAI()


class GptOpenAI:
    def __init__(self, model: str):
        self.model = model
        self.client = OpenAI()

    def generate(self, messages: list[Msg], tools: list[Tool] = None) -> AssistantMsg:
        messages = [m.to_openai() for m in messages]
        if tools is not None:
            tools = [t.openai_schema for t in tools]
        completion = self.client.chat.completions.create(
            messages=messages, model=self.model, tools=tools
        )
        return self._choice_to_msg(completion.choices[0])

    @staticmethod
    def _choice_to_msg(choice: Choice):
        return AssistantMsg(content=choice.message.content, tool_calls=choice.message.tool_calls)
