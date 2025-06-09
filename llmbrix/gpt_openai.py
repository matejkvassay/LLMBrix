from typing import Optional, Type, TypeVar, cast

from openai import OpenAI
from openai.types.responses import ResponseFunctionToolCall
from pydantic import BaseModel

from llmbrix.exceptions import OpenAIResponseError
from llmbrix.gpt_response import GptResponse
from llmbrix.msg import AssistantMsg, Msg, ToolRequestMsg
from llmbrix.tool import Tool

T = TypeVar("T", bound=BaseModel)
DEFAULT_TIMEOUT = 60


class GptOpenAI:
    """
    Wraps OpenAI GPT responses API.

    Expects "OPENAI_API_KEY=<your token>" env variable to be set.
    """

    def __init__(
        self,
        model: str = None,
        tools: list[Tool] = None,
        output_format: Optional[Type[T]] = None,
        api_timeout: int = DEFAULT_TIMEOUT,
        **responses_kwargs,
    ):
        """
        Parameters passed here will be set as defaults.

        Any value passed to these parameters in `generate()` will override these defaults.

        Note `model` has to be set either here or in `generate()` function.

        :param model: name of GPT model to use
        :param tools: (optional) list of Tool child instances to register to LLM as tools to be used
        :param output_format: (optional) Pydantic BaseModel instance to define output format of the LLM.
        :param api_timeout: timeout for OpenAI API in seconds. Default is 60s
        :param responses_kwargs: (optional) any additional kwargs to be passed to responses API.
                                 Note if output format is defined responses.parse is used.

        """
        self.model = model
        self.tools = tools
        self.output_format = output_format
        self.api_timeout = api_timeout
        self.responses_kwargs = responses_kwargs
        self.client = OpenAI()

    def __call__(self, *args, **kwargs) -> GptResponse:
        """
        Calls `generate()` method with provided args and kwargs.

        See docstring of `generate()` for supported args and kwargs values and return and raises info.
        """
        return self.generate(*args, **kwargs)

    def generate(
        self,
        messages: list[Msg],
        model: str = None,
        tools: list[Tool] = None,
        output_format: Optional[Type[T]] = None,
        api_timeout: int = None,
        **responses_kwargs,
    ) -> GptResponse:
        """
        Generates response from LLM. Supports tool calls and structured outputs.

        All parameters except messages can also be set in __init__() to define defaults.
        If provided here, they override those defaults.

        :param messages: list of messages for LLM to be used as input.
        :param model: name of GPT model to use
        :param tools: (optional) list of Tool child instances to register to LLM as tools to be used
        :param output_format: (optional) Pydantic BaseModel instance to define output format of the LLM.
        :param api_timeout: timeout for OpenAI API in seconds. Default is set to 60s.
        :param responses_kwargs: (optional) any additional kwargs to be passed to responses API.
                                 Note if output format is defined responses.parse is used.
                                 If output format is not defined responses.create is used.

        :return: GptResponse object (contains AssistantMsg and tool calls list).

        :raises OpenAIResponseError: if an error field is returned from OpenAI responses API call
        """
        model = model or self.model
        tools = tools or self.tools
        output_format = output_format or self.output_format
        api_timeout = self.api_timeout if api_timeout is None else api_timeout
        responses_kwargs = {**self.responses_kwargs, **responses_kwargs}
        if not model:
            raise ValueError(
                "No model name has been provided. Either set default model name in __init__() or pass "
                "it into this function."
            )

        messages = [m.to_openai() for m in messages]
        tool_schemas = [t.openai_schema for t in tools] if tools else []

        if output_format is None:
            response = self.client.responses.create(
                input=messages, model=model, tools=tool_schemas, timeout=api_timeout, **responses_kwargs
            )
        else:
            response = self.client.responses.parse(
                input=messages,
                model=model,
                tools=tool_schemas,
                text_format=output_format,
                timeout=api_timeout,
                **responses_kwargs,
            )
        if response.error:
            raise OpenAIResponseError(
                f"OpenAI API error — code: {getattr(response.error, 'code', 'unknown')}, "
                f"message: {getattr(response.error, 'message', 'No message provided')}"
            )
        tool_call_requests = [
            ToolRequestMsg.from_openai(t) for t in response.output if isinstance(t, ResponseFunctionToolCall)
        ]

        if output_format is None:
            assistant_msg = AssistantMsg(content=response.output_text)

        else:
            parsed = cast(Optional[T], response.output_parsed)
            content = parsed.model_dump(mode="json") if parsed else None
            assistant_msg = AssistantMsg(content=content, content_parsed=parsed)

        return GptResponse(message=assistant_msg, tool_calls=tool_call_requests)
