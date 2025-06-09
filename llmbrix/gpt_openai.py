from typing import Optional, Type, TypeVar, cast

from openai import OpenAI
from openai.types.responses import ResponseFunctionToolCall
from pydantic import BaseModel

from llmbrix.gpt_response import GptResponse
from llmbrix.msg import AssistantMsg, Msg, ToolRequestMsg
from llmbrix.tool import Tool

T = TypeVar("T", bound=BaseModel)


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

    def generate(
        self, messages: list[Msg], tools: list[Tool] = None, output_format: Type[T] = None, **responses_kwargs
    ) -> GptResponse:
        """
        Generates response from LLM.
        Tool calls are supported.
        Structured outputs are not supported when passing tools (without tools use "generate_structured()" method).

        :param messages: list of messages for LLM to be used as input.
        :param tools: (optional) list of Tool child instances to register to LLM as tools to be used
        :param output_format: (optional) Pydantic BaseModel instance to define output format of the LLM.
        :param responses_kwargs: (optional) any additional kwargs to be passed to responses API.
                                 Note if output format is defined responses.parse is used.
                                 If output format is not defined responses.create is used.

        :return: GptResponse object (contains AssistantMsg and tool calls list).
        """
        messages = [m.to_openai() for m in messages]
        if tools is not None:
            tools = [t.openai_schema for t in tools]
        else:
            tools = []

        if output_format is None:
            response = self.client.responses.create(input=messages, model=self.model, tools=tools, **responses_kwargs)
        else:
            response = self.client.responses.parse(
                input=messages, model=self.model, tools=tools, text_format=output_format, **responses_kwargs
            )
        if response.error:
            raise RuntimeError(
                f"Error during OpenAI API call: " f"code={response.error}, " f'msg="{response.error.message}"'
            )

        tool_call_requests = [
            ToolRequestMsg.from_openai(t) for t in response.output if isinstance(t, ResponseFunctionToolCall)
        ]

        if output_format is None:
            assistant_msg = AssistantMsg(content=response.output_text)

        else:
            parsed: Optional[T] = response.output_parsed
            content = None
            if parsed is not None:
                parsed = cast(T, parsed)
                content = parsed.model_dump(mode="json")
            assistant_msg = AssistantMsg(content=content, content_parsed=parsed)

        return GptResponse(message=assistant_msg, tool_calls=tool_call_requests)
