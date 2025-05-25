import logging

from openai import OpenAI

from llmbrix.msg import AssistantMsg, MsgBase
from llmbrix.tools import ToolBase

logger = logging.getLogger(__name__)
client = OpenAI()


class GPT:
    def __init__(self, model_name: str = "gpt-4o-mini", completion_kwargs=None):
        """
        :param model_name: Name of model for OpenAI API.
        :param completion_kwargs: Default completions API kwargs that will be used
                                  with every generate() request.
        """
        self.model = model_name
        self.completion_kwargs = completion_kwargs if completion_kwargs is not None else dict()
        self.client = OpenAI()

    def generate(
        self, messages: list[MsgBase], tools: list[ToolBase] | None = None, n=1, **completion_kwargs
    ) -> AssistantMsg | list[AssistantMsg]:
        """
        :param messages: list of MsgBase objects
        :param tools: optional, list of ToolBase objects, these tools will be passed to GPT
        :param n: default 1, how many different completions to generate
        :param completion_kwargs: dict, any additional completions API kwargs to set.
                                  Constructor kwargs will be updated with these.
                                  Overlaps are not checked.
        :return:
            If n==1, will return 1 AssistantMsg.
            If n>1 will return list of AssistantMsg objects.
        """
        messages = [m.api_dict() for m in messages]
        kwargs = self.completion_kwargs.copy()
        kwargs.update(completion_kwargs)
        if tools is not None:
            tools = [t.api_dict() for t in tools]
        completion = self.client.chat.completions.create(
            messages=messages, model=self.model, tools=tools, n=n, **kwargs
        )
        gpt_responses = [AssistantMsg.from_choice(choice) for choice in completion.choices]
        if n == 1:
            return gpt_responses[0]
        return gpt_responses
