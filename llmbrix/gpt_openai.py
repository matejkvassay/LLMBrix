import json
from typing import Optional, Type, TypeVar, cast

from openai import AzureOpenAI, OpenAI, OpenAIError
from openai.types.responses import ResponseFunctionToolCall
from pydantic import BaseModel

from llmbrix.exceptions import OpenAIResponseError
from llmbrix.gpt_response import GptResponse
from llmbrix.msg import AssistantMsg, Msg, ToolRequestMsg
from llmbrix.tool import Tool

T = TypeVar("T", bound=BaseModel)


class GptOpenAI:
    """
    GPT wrapper used to generate tokens via OpenAI API.
    Supports non-reasoning GPT models, tool calling and structured outputs.
    Internally uses responses API.
    """

    def __init__(
        self,
        model: str,
        openai_client: OpenAI | AzureOpenAI = None,
        tools: list[Tool] = None,
        output_format: Optional[Type[T]] = None,
        api_timeout: int = 60,
        **responses_kwargs,
    ):
        """
        Parameters passed here will be set as defaults.
        Any value passed to these parameters in `generate()` will override these defaults.

        :param model: name of GPT model to use. Reasoning models are not supported.
        :param openai_client: `OpenAI` or `AzureOpenAI` object from official OpenAI SDK.
                              If not provided then:
                                  1. `OpenAI` client is initialized from `OPENAI_API_KEY` env var.
                                  2. If `OPENAI_API_KEY` not provided either then` AzureOpenAI` client is
                                     initialized from env vars. At minimum set following vars:
                                        - `AZURE_OPENAI_API_KEY`
                                        - `OPENAI_API_VERSION`
                                        - `AZURE_OPENAI_ENDPOINT`
                              Refer to official SDK `OpenAI` and `AzureOpenAI` class docs for more details.
        :param tools: (optional) list of Tool instances to register to LLM as tools to be used
        :param output_format: (optional) Pydantic BaseModel instance to define structured output from LLM
        :param api_timeout: timeout for OpenAI API in seconds. Default is 60s
        :param responses_kwargs: (optional) any additional kwargs to be passed to responses API.
        """
        self.model = model
        self.tools = tools
        self.output_format = output_format
        self.api_timeout = api_timeout
        self.responses_kwargs = responses_kwargs
        if openai_client:
            self.client = openai_client
        else:
            try:
                self.client = OpenAI()
            except OpenAIError:
                self.client = AzureOpenAI()

    @classmethod
    def from_openai(cls, model: str, api_key: str, **kwargs) -> "GptOpenAI":
        """
        Initialize GptOpenAI instance with standard OpenAI API.

        :param model: name of GPT model to use. Reasoning models are not supported.
        :param api_key: OpenAI API key.
        :param kwargs: Kwargs passed to __init__ method. See DocString of __init__ for details.

        :return: Instance of GptOpenAI with standard OpenAI client.
        """
        client = OpenAI(api_key=api_key)
        return cls(model=model, openai_client=client, **kwargs)

    @classmethod
    def from_azure_openai(
        cls,
        model: str,
        api_key: str,
        api_version: str,
        azure_endpoint: str,
        azure_deployment: str,
        **kwargs,
    ) -> "GptOpenAI":
        """
        Initialize GptOpenAI instance from standard Azure OpenAI API args.

        :param model: name of GPT model to use. Reasoning models are not supported.
        :param api_key: Azure OpenAI API key.
        :param api_version: Azure OpenAI API version.
        :param azure_endpoint: Azure OpenAI API endpoint.
        :param azure_deployment: Azure OpenAI API deployment.
        :param kwargs: Kwargs passed to __init__ method. See DocString of __init__ for details.

        :return: Instance of GptOpenAI with AzureOpenAI client.
        """
        client = AzureOpenAI(
            api_key=api_key, api_version=api_version, azure_endpoint=azure_endpoint, azure_deployment=azure_deployment
        )
        return cls(model=model, openai_client=client, **kwargs)

    def __call__(self, *args, **kwargs) -> GptResponse:
        """
        Calls `generate()` method with provided args and kwargs.

        See docstring of `generate()` for supported args and kwargs values and return and raises info.
        """
        return self.generate(*args, **kwargs)

    def generate(
        self,
        messages: list[Msg],
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
        :param tools: (optional) list of Tool child instances to register to LLM as tools to be used
        :param output_format: (optional) Pydantic BaseModel instance to define structured output from LLM
        :param api_timeout: timeout for OpenAI API in seconds. Default is set to 60s.
        :param responses_kwargs: (optional) any additional kwargs to be passed to responses API.
                                 Note if output format is defined responses.parse is used.
                                 If output format is not defined responses.create is used.

        :return: GptResponse object (contains .message, .tool_calls).
                 In case LLM requests tool calls message field might be None.
                 In case there is no tool calls the tool_calls field will be None.

        :raises OpenAIResponseError: if an error field is returned from OpenAI responses API call
        """
        tools = tools or self.tools
        output_format = output_format or self.output_format
        api_timeout = self.api_timeout if api_timeout is None else api_timeout
        responses_kwargs = {**self.responses_kwargs, **responses_kwargs}

        messages = [m.to_openai() for m in messages]
        tool_schemas = [t.openai_schema for t in tools] if tools else []

        if output_format is None:
            response = self.client.responses.create(
                input=messages, model=self.model, tools=tool_schemas, timeout=api_timeout, **responses_kwargs
            )
        else:
            response = self.client.responses.parse(
                input=messages,
                model=self.model,
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
            content = json.dumps(parsed.model_dump(mode="json")) if parsed else None
            assistant_msg = AssistantMsg(content=content, content_parsed=parsed)
        if not assistant_msg.content:
            assistant_msg = None
        if not tool_call_requests:
            tool_call_requests = None
        if assistant_msg is None and tool_call_requests is None:
            raise RuntimeError("Request unsuccessful. Neither tool call nor assistant message was returned by LLM.")
        return GptResponse(message=assistant_msg, tool_calls=tool_call_requests)
