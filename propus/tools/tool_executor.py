import logging
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from google.genai import types

from propus.tools.base_tool import BaseTool
from propus.tools.tool_output import ToolOutput

logger = logging.getLogger(__name__)


class ToolExecutor:
    def __init__(self, tools: list[BaseTool], n_workers: int = 1, timeout: int | None = 60):
        self.tool_index = {t.name: t for t in tools}
        self.n_workers = n_workers
        self.timeout = timeout

    def execute(self, tool_requests: list[types.FunctionCall]) -> list[ToolOutput]:
        if self.n_workers == 1:
            return [self._execute_single_tool_call(req) for req in tool_requests]
        with ThreadPoolExecutor(max_workers=self.n_workers) as executor:
            futures = [executor.submit(self._execute_single_tool_call, req) for req in tool_requests]
            results = []
            for i, future in enumerate(futures):
                try:
                    res = future.result(timeout=self.timeout)
                    results.append(res)
                except TimeoutError:
                    req = tool_requests[i]
                    results.append(self._handle_timeout_error(req))
            return results

    def _execute_single_tool_call(self, req: types.FunctionCall) -> ToolOutput:
        tool = self.tool_index.get(req.name, None)
        if tool is None:
            return self._handle_unknown_tool(req=req)
        try:
            args = req.args if isinstance(req.args, dict) else {}
            tool_output = tool.execute(**args)
            if not isinstance(tool_output, ToolOutput):
                return self._handle_incorrect_output_type(req=req, tool_output=tool_output)
            if not tool_output.result:
                return self._handle_empty_tool_result(req=req)
            return tool_output
        except Exception as ex:
            return self._handle_tool_execution_error(req=req, ex=ex)

    def _handle_unknown_tool(self, req: types.FunctionCall) -> ToolOutput:
        logger.error(f'LLM tool "{req.name}" not found.')
        return ToolOutput(
            success=False,
            result={
                "error": f'Tool named "{req.name}" not found. Names of available tools : '
                f'{list(self.tool_index.keys())}"'
            },
            debug_trace={"error": "Tool not found.", "tool_request": req.model_dump(mode="json")},
        )

    @staticmethod
    def _handle_empty_tool_result(req: types.FunctionCall) -> ToolOutput:
        logger.error(
            f'LLM tool "{req.name}" returned empty result. '
            f'Tool request: {req.model_dump(mode="json", include={"name", "args"})}'
        )
        return ToolOutput(
            success=False,
            result={"error": f'Tool "{req.name}" returned empty result.'},
            debug_trace={"error": "Tool returned empty result.", "tool_request": req.model_dump(mode="json")},
        )

    @staticmethod
    def _handle_incorrect_output_type(req: types.FunctionCall, tool_output: Any) -> ToolOutput:
        actual_type = type(tool_output).__name__
        logger.error(f'Tool "{req.name}" violated contract: expected ToolOutput, got {actual_type}.')
        return ToolOutput(
            success=False,
            result={"error": f'Internal error: Tool "{req.name}" returned an invalid data format.'},
            debug_trace={
                "error": "Incorrect output type from tool implementation.",
                "expected_type": "ToolOutput",
                "received_type": actual_type,
                "received_value": str(tool_output),
                "tool_request": req.model_dump(mode="json"),
            },
        )

    @staticmethod
    def _handle_tool_execution_error(req: types.FunctionCall, ex: Exception) -> ToolOutput:
        logger.error(
            f"Exception raised during tool execution. "
            f'Tool request: {req.model_dump(mode="json", include={"name", "args"})}',
            exc_info=ex,
        )
        return ToolOutput(
            success=False,
            result={
                "error": f'Execution of tool "{req.name}" failed.',
                "error_type": type(ex).__name__,
                "details": str(ex),
                "hint": "Refer to the tool definition and ensure all "
                "required arguments are present and correctly typed.",
            },
            debug_trace={
                "error": "Exception during tool execution.",
                "tool_request": req.model_dump(mode="json"),
                "stack_trace": traceback.format_exc(),
            },
        )

    def _handle_timeout_error(self, req: types.FunctionCall) -> ToolOutput:
        logger.error(
            f'Tool "{req.name}" timed out after {self.timeout} seconds. '
            f'Tool request: {req.model_dump(mode="json", include={"name", "args"})}'
        )
        return ToolOutput(
            success=False,
            result={
                "error": f'Tool "{req.name}" timed out.',
                "details": f"The execution exceeded the maximum allowed time of {self.timeout}s.",
            },
            debug_trace={
                "error": "TimeoutError",
                "timeout_limit": self.timeout,
                "tool_request": req.model_dump(mode="json"),
            },
        )
