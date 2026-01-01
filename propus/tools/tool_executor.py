import logging
import traceback

from google.genai import types

from propus.tools.base_tool import BaseTool
from propus.tools.tool_output import ToolOutput

logger = logging.getLogger(__name__)


class ToolExecutor:
    def __init__(self, tools: list[BaseTool]):
        self.tool_index = {t.name: t for t in tools}

    def execute(self, tool_requests: list[types.FunctionCall]) -> list[ToolOutput]:
        outputs = []
        for req in tool_requests:
            tool = self.tool_index.get(req.name, None)
            if tool is None:
                outputs.append(self._handle_unknown_tool(req=req))
                continue
            try:
                args = req.args or {}
                tool_output = tool.execute(**args)
                if not tool_output.result:
                    outputs.append(self._handle_empty_tool_result(req=req))
                    continue
                outputs.append(tool_output)
            except Exception as ex:
                outputs.append(self._handle_tool_execution_error(req=req, ex=ex))
        return outputs

    def _handle_unknown_tool(self, req: types.FunctionCall) -> ToolOutput:
        logger.error(f'LLM tool "{req.name}" not found.')
        return ToolOutput(
            result={
                "error": f'Tool named "{req.name}" not found. Names of available tools : '
                f'{list(self.tool_index.keys())}"'
            },
            debug_trace={"error": "Tool not found.", "tool_request": req.model_dump()},
        )

    @staticmethod
    def _handle_empty_tool_result(req: types.FunctionCall) -> ToolOutput:
        logger.error(
            f'LLM tool "{req.name}" returned empty result. ' f'Tool request: {req.model_dump(include={"name", "args"})}'
        )
        return ToolOutput(
            result={"error": f'Tool "{req.name}" returned empty result.'},
            debug_trace={"error": "Tool returned empty result.", "tool_request": req.model_dump()},
        )

    @staticmethod
    def _handle_tool_execution_error(req: types.FunctionCall, ex: Exception) -> ToolOutput:
        logger.error(
            f'Exception raised during tool execution. Tool request: {req.model_dump(include={"name", "args"})}',
            exc_info=ex,
        )
        return ToolOutput(
            result={
                "error": f'Execution of tool "{req.name}" failed.',
                "error_type": type(ex).__name__,
                "details": str(ex),
                "hint": "Refer to the tool definition and ensure all "
                "required arguments are present and correctly typed.",
            },
            debug_trace={
                "error": "Exception during tool execution.",
                "tool_request": req.model_dump(),
                "stack_trace": traceback.format_exc(),
            },
        )
