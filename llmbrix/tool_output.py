from typing import Any

from pydantic import BaseModel


class ToolOutput(BaseModel):
    """
    Output of tool execution.

    Contains:
     - content = content with str output of tool, visible to LLM
     - meta = (optional) additional metadata appended during the tool execution, not visible to LLM
    """

    content: str
    meta: dict[str, Any] = {}
