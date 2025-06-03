from typing import Optional, Type, TypeVar

from openai import OpenAI
from openai.types.responses import ResponseFunctionToolCall
from pydantic import BaseModel

from llmbrix.msg import AssistantMsg, Msg, ToolRequestMsg
from llmbrix.tool import Tool

T = TypeVar("T", bound=BaseModel)


class GptResponse(BaseModel):
    """
    Response from a GPT model used for non-structured LLM outputs.
    Contains assistant message and list of tool calls (potentially empty list).
    """

    message: AssistantMsg
    tool_calls: list[ToolRequestMsg]


class GptOpenAI:
    """
    Wraps OpenAI GPT responses API.
    Enables to generate tokens using GPT LLM models.

    For unstructured responses and tool calls use:
    `generate()`

    For structured LLM output use:
    `generate_structured()`

    Expects "OPENAI_API_KEY=<your token>" env variable to be set.
    """

    def __init__(self, model: str):
        """
        :param model: str model name
        """
        self.model = model
        self.client = OpenAI()

    def generate(self, messages: list[Msg], tools: list[Tool] = None) -> GptResponse:
        """
        Generates response from LLM.
        Tool calls are supported.
        Structured outputs are not supported when passing tools (without tools use "generate_structured()" method).

        :param messages: list of messages for LLM to be used as input.
        :param tools: (optional) list of Tool child instances to register to LLM as tools to be used

        :return: GptResponse object (contains AssistantMsg and tool calls list).
        """
        messages = [m.to_openai() for m in messages]
        if tools is not None:
            tools = [t.openai_schema for t in tools]
        else:
            tools = []
        response = self.client.responses.create(input=messages, model=self.model, tools=tools)
        if response.error:
            raise RuntimeError(
                f"Error during OpenAI API cal: " f"code={response.error}, " f'msg="{response.error.message}"'
            )
        tool_call_requests = [
            ToolRequestMsg.from_openai(t) for t in response.output if isinstance(t, ResponseFunctionToolCall)
        ]
        return GptResponse(message=AssistantMsg(content=response.output_text), tool_calls=tool_call_requests)

    def generate_structured(self, messages: list[Msg], output_format: Type[T]) -> Optional[T]:
        """
        Generate response with LLM.
        Uses structured output - LLM output is formatted into specific Pydantic model pass in "output_format".
        Tool calls are not supported when using structured outputs.

        :param messages: list of messages for LLM to be used as input.
        :param output_format: Pydantic BaseModel instance.

        :return: Filled BaseModel instance or None if generation failed.
        """
        messages = [m.to_openai() for m in messages]
        response = self.client.responses.parse(input=messages, model=self.model, text_format=output_format)
        if response.error:
            raise RuntimeError(
                f"Error during OpenAI API cal: " f"code={response.error}, " f'msg="{response.error.message}"'
            )
        return response.output_parsed
