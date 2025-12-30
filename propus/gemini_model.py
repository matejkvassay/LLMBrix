import os
from typing import Type

from google.genai import Client, types
from pydantic import BaseModel

from propus.msg import BaseMsg, ModelMsg


class GeminiModel:
    def __init__(self, gemini_client: Client | None, model_name: str):
        if not gemini_client:
            if not os.environ.get("GOOGLE_API_KEY"):
                raise ValueError("You have to either set env var GOOGLE_API_KEY or pass a gemini_client object.")
            gemini_client = Client()
        self.gemini_client = gemini_client
        self.model_name = model_name

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
        system_instruction: str | None = None,
        tools: list[types.Tool] | None = None,
        response_schema: Type[BaseModel] | None = None,
    ):
        cfg = types.GenerateContentConfig()
        if system_instruction:
            cfg.system_instruction = system_instruction
        if response_schema:
            cfg.update(
                {
                    "response_mime_type": "application/json",
                    "response_json_schema": response_schema.model_json_schema(),
                }
            )
        response = self.gemini_client.models.generate_content(model=self.model_name, contents=messages, config=cfg)
        parsed = None
        if response_schema:
            parsed = response.parsed
        return ModelMsg(parts=response.parts, parsed=parsed)

    def generate_from_content_cfg(self, cfg: types.GenerateContentConfig):
        pass
