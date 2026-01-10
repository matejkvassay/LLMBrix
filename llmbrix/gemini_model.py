import logging
import os
from typing import Optional, Type

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
        gemini_client: Optional[Client] = None,
        model: str = "gemini-2.5-flash-lite",
        system_instruction: Optional[str] = None,
        tools: Optional[list[BaseTool] | types.ToolListUnion] = None,
        response_schema: Optional[Type[BaseModel]] = None,
        json_mode: bool = False,
        max_output_tokens: Optional[int] = SAFETY_MAX_TOKENS_DEFAULT,
        include_thoughts: bool = False,
        thinking_budget: Optional[int] = None,
        thinking_level: types.ThinkingLevel | None = None,
        temperature: Optional[float] = 0.0,
        **extra_config_kwargs,
    ):
        """
        Args:
            gemini_client: Client object from google-genai SDK.
                           If not provided then it will be automatically created from GOOGLE_API_KEY env var.
            model: Name of model to use e.g. "gemini-2.5-flash-lite"
            system_instruction: Static system instruction. Can be overridden with instruction passed to generate().
            tools: List of tools for LLM to use.
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
            temperature: Float temperature setting, controls randomness of output. Set to 0 by default.
            extra_config_kwargs: Extra config kwargs to be set to types.GenerateContentConfig object construction
        """
        if not gemini_client:
            if not os.environ.get("GOOGLE_API_KEY"):
                raise ValueError("You have to either set env var GOOGLE_API_KEY or pass a gemini_client object.")
            gemini_client = Client()
        self.gemini_client = gemini_client
        self.model = model
        self.generation_config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            max_output_tokens=max_output_tokens,
            response_schema=response_schema,
            response_mime_type="application/json" if response_schema or json_mode else "text/plain",
            temperature=temperature,
            tools=tools,
            thinking_config=types.ThinkingConfig(
                include_thoughts=include_thoughts, thinking_budget=thinking_budget, thinking_level=thinking_level
            ),
            **extra_config_kwargs,
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

    def generate(
        self,
        messages: list[BaseMsg],
        system_instruction: Optional[str] = None,
        response_schema: Optional[Type[BaseModel]] = None,
        tools: Optional[list[BaseTool] | types.ToolListUnion] = None,
        tool_call_required: bool = False,
        **extra_config_kwargs,
    ):
        """
        Generate tokens Gemini API.

        Args:
            messages: Chat history consisting of BaseMsg objects.
                      Has to end with UserMsg (current request to respond to).
            system_instruction: System instruction. Overrides instruction set in constructor.
            response_schema: LLM will predict output in this structure, parsed model filled with values can be found
                 in .parsed attribute of the returned ModelMsg. Overrides response schema set in constructor.
            tools: List of tools for LLM to use. Overrides list of tools set in constructor.
            tool_call_required: If True LLM will be forced to use a tool call (tool mode set to "ANY")
            extra_config_kwargs: Extra config kwargs to be set to types.GenerateContentConfig object construction.
                                 Overrides constructor - provided generation config kwargs.
                                 N ote some args might not work depending on other settings
                                 (e.g. ToolConfig is set automatically based on tool_call_required param.).

        Returns: ModelMsg object containing response from Gemini model.
        """
        generation_config = self.generation_config
        if system_instruction or tools or response_schema or extra_config_kwargs:
            system_instruction = system_instruction or generation_config.system_instruction
            tool_config = None
            if tools:
                mode = (
                    types.FunctionCallingConfigMode.ANY if tool_call_required else types.FunctionCallingConfigMode.AUTO
                )
                tool_config = types.ToolConfig(function_calling_config=types.FunctionCallingConfig(mode=mode))
            updated_config_fields = {
                "system_instruction": system_instruction,
                "tools": tools,
                "tool_config": tool_config,
            }
            if response_schema:
                updated_config_fields.update(
                    {"response_schema": response_schema, "response_mime_type": "application/json"}
                )
            updated_config_fields.update(extra_config_kwargs)
            generation_config = generation_config.model_copy(update=updated_config_fields)

        response = self.gemini_client.models.generate_content(
            model=self.model, contents=messages, config=generation_config
        )

        if not response.candidates or not response.candidates[0].content.parts:
            logger.warning(
                f"Gemini returned an empty response. "
                f"Finish reason: {response.candidates[0].finish_reason if response.candidates else 'Unknown'}"
            )
            return ModelMsg(parts=[])

        parsed = None
        if generation_config.response_schema:
            parsed = response.parsed

        return ModelMsg(parts=response.parts, parsed=parsed)
