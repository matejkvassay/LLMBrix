from typing import Any, Optional

from google.genai import types
from propus.msg.tool_msg import ToolMsg
from pydantic import BaseModel, JsonValue


class ToolOutput(BaseModel):
    """
    Output of .execute() function from the LLM tool.
    Contains outputs visible and invisible to LLM, other information and offers way to easily convert to ToolMsg.
    """

    success: bool  # Set to True if tool execution ok. Set to False in order to indicate tool execution failed.
    result: dict[str, JsonValue]  # output from tool execution visible to LLM, must be JSON serializable dict
    artifacts: Optional[dict[str, Any]] = None  # outputs not visible to LLM (e.g. generated plotly plot)
    debug_trace: Optional[dict[str, Any]] = None  # include details for application developers to be able to debug

    def to_tool_msg(self, tool_call: types.FunctionCall) -> ToolMsg:
        """
        Converts this tool execution output into a ToolMsg.

        Args:
            tool_call: FunctionCall tool call request related to this tool execution output.
        Returns: ToolMsg
        """
        return ToolMsg(tool_call=tool_call, result=self.result.copy())
