from typing import Any

from pydantic import BaseModel


class ToolOutput(BaseModel):
    """
    Output of tool execution.
    Contains:
     - content with str output of tool, visible to LLM
     - additional metadata appended during the execution, not visible to LLM
    """

    content: str
    meta: dict[str, Any] = {}
