from typing import TypeVar

from pydantic import BaseModel

from llmbrix.msg import AssistantMsg, ToolRequestMsg

T = TypeVar("T", bound=BaseModel)


class GptResponse(BaseModel):
    """
    Response from a GPT model.
    Contains assistant message and list of tool calls (potentially empty list).
    """

    message: AssistantMsg  # response message from LLM
    tool_calls: list[ToolRequestMsg]  # list of requested tool calls, can be and empty list
