from typing import Any, Optional

from pydantic import BaseModel


class Msg(BaseModel):
    """
    Base message class.
    """

    meta: Optional[dict[str, Any]] = None  # used to store any metadata / debug info not visible to LLM

    def to_openai(self) -> dict:
        """
        Transform this message to dict compatible with OpenAI API.
        Excludes meta field.

        :return: OpenAI API - compatible dict representing message.
        """
        exclude = ["meta"]
        return self.model_dump(exclude=set(exclude))
