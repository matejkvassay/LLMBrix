from typing import Any, Dict, Optional

from google.genai import types
from pydantic import BaseModel, Field, JsonValue

from propus.msg.tool_msg import ToolMsg


class ToolOutput(BaseModel):
    """
    Output of .execute() function from the LLM tool.
    Contains outputs visible and invisible to LLM, other information and offers way to easily convert to ToolMsg.
    """

    result: dict[str, JsonValue]  # output from tool execution visible to LLM, must be JSON serializable dict
    error: Optional[str] = None  # only fill if error occurs. If filled execution will be considered as failed.
    artifacts: Dict[str, Any] = Field(default_factory=dict)  # outputs not visible to LLM (e.g. generated plotly plot)
    debug_trace: Optional[Dict[str, Any]] = None  # include details for application developers to be able to debug

    def to_tool_msg(self, tool_call: types.FunctionCall) -> ToolMsg:
        """
        Converts this tool execution output into a ToolMsg.

        Args:
            tool_call: FunctionCall tool call request related to this tool execution output.
        Returns: ToolMsg
        """
        llm_payload = self.result.copy()
        if self.error:
            llm_payload["error"] = self.error
        return ToolMsg(tool_call=tool_call, result=llm_payload)
