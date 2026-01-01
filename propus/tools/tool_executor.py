import logging
import traceback
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Any

from google.genai import types

from propus.tools.base_tool import BaseTool
from propus.tools.tool_output import ToolOutput

logger = logging.getLogger(__name__)


class ToolExecutor:
    """
    Executes required tool calls via multi-threading and handles potential errors in LLM-friendly way.
    """

    def __init__(self, tools: list[BaseTool], n_workers: int = 4, timeout: int | None = 120):
        """
        Args:
            tools: List of tools to execute.
            n_workers: Number of threads to use.
            timeout: Timeout in seconds. If timeout is reached tool result will inform LLM about timeout error.
                     Beware zombie threads are possible when timeout is reached.
        """
        self.tool_index = {t.name: t for t in tools}
        self.n_workers = n_workers
        self.timeout = timeout
        self.executor = ThreadPoolExecutor(max_workers=n_workers)

    def execute(self, tool_requests: list[types.FunctionCall]) -> list[ToolOutput]:
        """
        Execute list of tool requests.

        Args:
            tool_requests: List of tool call requests from LLM.

        Returns: List of tool outputs in order equal to tool requests.
        """
        futures = [self.executor.submit(self._execute_single_tool_call, req) for req in tool_requests]
        results = []
        for i, future in enumerate(futures):
            req = tool_requests[i]
            try:
                res = future.result(timeout=self.timeout)
                results.append(res)
            except TimeoutError:
                results.append(self._handle_timeout_error(req))
            except Exception as ex:
                results.append(self._handle_tool_execution_error(req=req, ex=ex))

        return results

    def shutdown(self):
        """
        Call on application shutdown to free up OS threads.
        """
        self.executor.shutdown(wait=True)

    def _execute_single_tool_call(self, req: types.FunctionCall) -> ToolOutput:
        """
        Execute one single tool call.

        Args:
            req: Tool call request from LLM

        Returns: Tool call output
        """
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
        """
        Compose tool output when incorrect tool name was requested by the LLM.

        Args:
            req: Tool call request from LLM

        Returns: Tool call output informing LLM about the error
        """
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
        """
        Compose tool output when tool returned empty result (dict with no fields).

        Args:
            req: Tool call request from LLM

        Returns: Tool call output informing LLM about the error
        """
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
        """
        Handle situation where LLM tool returned incorrect output type.

        Args:
            req: Tool call request from LLM
            tool_output: Tool call output with incorrect result type

        Returns: Tool call output informing LLM about the error
        """
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
        """
        Prepare tool output for situation where tool raised exception during execute() function call

        Args:
            req: Tool call request from LLM
            ex: Exception raised during execute() function call

        Returns: Tool call output informing LLM about the error
        """
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
        """
        Prepare tool output for situation where tool execution times out.

        Args:
            req: Tool call request from LLM

        Returns: Tool call output informing LLM about the error

        """
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
