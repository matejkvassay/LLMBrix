import logging
from typing import Any

from google.genai import types

from llmbrix.msg.base_msg import BaseMsg
from llmbrix.msg.model_msg import ModelMsg

logger = logging.getLogger(__name__)

TOOL_ROLE_NAME = "function"


class ToolMsg(BaseMsg):
    """
    Message representing the result of a tool (function) execution.
    This is sent back to the LLM as the 'Function Response'.
    """

    def __init__(self, tool_call: types.FunctionCall, result: Any):
        """
        Args:
            tool_call: The FunctionCall object from ModelMsg.tool_calls.
                       Used to ensure the 'name' field is perfectly matched.
            result: The output of the function. Must be a dict (as per API spec).
                    If a non-dict is passed, it is wrapped in {'result': ...}.
        """
        if not isinstance(result, dict):
            logger.warning(f"Tool result for '{tool_call.name}' is not a dict. Wrapping it under 'result' key.")
            response_dict = {"result": result}
        else:
            response_dict = result
        part = types.Part.from_function_response(name=tool_call.name, response=response_dict)
        super().__init__(role=TOOL_ROLE_NAME, parts=[part])

    @classmethod
    def from_results(cls, model_msg: ModelMsg, results: list[Any]) -> list["ToolMsg"]:
        """
        Helper to create a list of ToolMsgs from a ModelMsg that requested multiple tool calls.

        Args:
            model_msg: The ModelMsg containing the requested tool calls.
            results: A list of return values from your local function executions.
                     Must match the order of model_msg.tool_calls.
        """
        calls = model_msg.tool_calls
        if len(calls) != len(results):
            raise ValueError(f"Count mismatch: Model called {len(calls)} tool_calling, but got {len(results)} results.")

        return [cls(tool_call=call, result=res) for call, res in zip(calls, results)]
