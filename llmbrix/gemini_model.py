import logging
import os
from typing import Type

from google.genai import Client, types
from pydantic import BaseModel

from llmbrix.msg import BaseMsg, ModelMsg
from llmbrix.tool_calling import BaseTool

logger = logging.getLogger(__name__)

SAFETY_MAX_TOKENS_DEFAULT = 10000


class GeminiModel:
    """
    Wrapper around Gemini API suited for chat and agentic applications.
    """

    def __init__(
        self,
        gemini_client: Client | None,
        model_name: str,
        tools: list[BaseTool] | types.ToolListUnion | None = None,
        system_instruction: str | None = None,
        response_schema: Type[BaseModel] | None = None,
        json_mode: bool = False,
        max_output_tokens: int | None = SAFETY_MAX_TOKENS_DEFAULT,
        include_thoughts: bool = False,
        thinking_budget: int = None,
        thinking_level: types.ThinkingLevel | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
    ):
        """
        Args:
            gemini_client: google-genai SDK client
            model_name: Name of model to use e.g. "gemini-2.5-flash-lite"
            tools: List of BaseTool instances.
            system_instruction: Static system instruction. Can be overridden with instruction passed to generate().
            json_mode: If True LLM will respond JSON outputs, otherwise plaintext outputs will be received.
            response_schema: LLM will predict output in this structure, parsed model filled with values can be found
                             in .parsed attribute of the returned ModelMsg.
            max_output_tokens: Hard limit on maximum output tokens LLM can produce.
                               By default, set to a limit to avoid cost explosion incidents.
                               Can be set to None for infinite generation.
            include_thoughts: Include LLM internal reasoning tokens in the response. If enabled tokens can be found
                              inside ModelMsg.segments as one of the "THOUGHT" type outputs.
            thinking_budget: Gemini 2 only.
                             Set hard limit on allowed number of thinking tokens.
                             Possible values:
                                a) 0 => thinking disabled,
                                b) -1 => automatic
                                c) int[1,...,N] => limit thinking token count to this num.
                             Legacy parameter for Gemini 2.5 models, deprecated in Gemini 3.
            thinking_level: Gemini 3 only.
                            Set thinking level for Gemini 3 models.
            temperature: Float temperature setting, controls randomness of output.
            top_p: If specified, nucleus sampling will be used.
            top_k: If specified, top-k sampling will be used.
        """
        if not gemini_client:
            if not os.environ.get("GOOGLE_API_KEY"):
                raise ValueError("You have to either set env var GOOGLE_API_KEY or pass a gemini_client object.")
            gemini_client = Client()
        self.gemini_client = gemini_client
        self.model_name = model_name
        self.generation_config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            max_output_tokens=max_output_tokens,
            response_schema=response_schema,
            response_mime_type="application/json" if response_schema or json_mode else "text/plain",
            temperature=temperature,
            tools=tools,
            top_k=top_k,
            top_p=top_p,
            thinking_config=types.ThinkingConfig(
                include_thoughts=include_thoughts, thinking_budget=thinking_budget, thinking_level=thinking_level
            ),
        )

    @classmethod
    def from_gemini_api_key(cls, google_api_key: str | None = None, **kwargs):
        """
        Constructs LlmAgent from API key, takes care of initialization of Gemini API client.

        You have to either set env var GOOGLE_API_KEY or pass google_api_key parameter.

        Args:
            google_api_key: str Gemini API key
            **kwargs: will be passed to __init__, see docs of __init__ for reference.

        Returns: Initialized instance of LlmAgent
        """
        if (not google_api_key) and (not os.environ.get("GOOGLE_API_KEY")):
            raise ValueError("You have to either set env var GOOGLE_API_KEY or pass google_api_key parameter.")
        gemini_client = Client(api_key=google_api_key)
        return cls(gemini_client=gemini_client, **kwargs)

    def generate(self, messages: list[BaseMsg], system_instruction: str | None = None, disable_tools=False):
        """
        Generate tokens Gemini API.

        Args:
            messages: Chat history consisting of BaseMsg objects.
                      Has to end with UserMsg (current request to respond to).
            system_instruction: System instruction, overrides instruction set in constructor.
            disable_tools: Disable LLM tools, sets them to None in generation config for this request.

        Returns: ModelMsg object containing response from Gemini model.

        """
        generation_config = self.generation_config
        if system_instruction or disable_tools:
            system_instruction = system_instruction or generation_config.system_instruction
            tools = None if disable_tools else generation_config.tools
            generation_config = generation_config.model_copy(
                update={"system_instruction": system_instruction, "tools": tools}
            )

        response = self.gemini_client.models.generate_content(
            model=self.model_name, contents=messages, config=generation_config
        )
        parsed = None
        if generation_config.response_schema:
            parsed = response.parsed

        return ModelMsg(parts=response.parts, parsed=parsed)
