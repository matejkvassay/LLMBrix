from typing import Optional

from pydantic import BaseModel

from llmbrix.msg.msg import Msg


class AssistantMsg(Msg):
    """
    Message containing response form LLM assistant.
    """

    content: Optional[str] = None  # str content response generated by LLM
    content_parsed: Optional[BaseModel] = None  # only used with structured outputs
    role: str = "assistant"
