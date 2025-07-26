from typing import Optional, TypeVar

from pydantic import BaseModel, model_validator

from llmbrix.msg import AssistantMsg, ToolRequestMsg

T = TypeVar("T", bound=BaseModel)


class GptResponse(BaseModel):
    """
    Response from a GPT model.
    Can contain assistant message and list of tool calls.
    Behavior of responses API:
     - if no tool calls are required message can be None
     - if there are tool calls message is usually None but its not guaranteed, sometimes message can be supplied
     - there should never be a case when message and tool calls are both None
    """

    message: Optional[AssistantMsg] = None
    tool_calls: Optional[list[ToolRequestMsg]] = None

    @model_validator(mode="after")
    def check_message_or_tool_calls(cls, values):
        if values.message is None and not values.tool_calls:
            raise ValueError("Either 'message' or 'tool_calls' must be set.")
        return values
