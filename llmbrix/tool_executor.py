import json
import traceback
from json import JSONDecodeError

from jinja2 import Template

from llmbrix.msg import ToolOutputMsg, ToolRequestMsg
from llmbrix.tool import Tool
from llmbrix.tool_output import ToolOutput

DEFAULT_TOOL_ERROR_TEMPLATE = Template("Error during tool execution: {{error}}")


class ToolExecutor:
    """
    Handles execution of tool calls requested by LLM.
    """

    def __init__(self, tools: list[Tool], error_template: Template = DEFAULT_TOOL_ERROR_TEMPLATE):
        """
        :param tools: List of Tool child instances.
        :param error_template: Jinja template containing 1 variable "error" where exception str will be inserted.
        """
        self.tool_idx = {t.name: t for t in tools}
        self.error_template = error_template

    def __call__(self, tool_calls: list[ToolRequestMsg]) -> list[ToolOutputMsg]:
        return self.execute_tool_calls(tool_calls)

    def execute_tool_calls(self, tool_calls: list[ToolRequestMsg]) -> list[ToolOutputMsg]:
        """
        Execute tool calls.

        If execution of tool successful then it will contain result as content and metadata with additional
        details/artifacts.

        If execution of tool fails it will contain formatted error template with exception and error stack
        trace as metadata.

        :param tool_calls: list of ToolRequestMsg objects
        :return: list of ToolOutputMsg objects.
        """
        return [self._execute_tool_call(req) for req in tool_calls]

    def _execute_tool_call(self, tool_call: ToolRequestMsg) -> ToolOutputMsg:
        """
        Execute single tool call.

        If execution of tool successful then it will contain result as content and metadata with additional
        details/artifacts.

        If execution of tool fails it will contain formatted error template with exception and error stack
        trace as metadata.

        :param tool_call: ToolRequestMsg object
        :return: ToolOutputMsg
        """
        name = tool_call.name
        kwargs = tool_call.arguments
        assert isinstance(kwargs, str)
        try:
            tool = self.tool_idx.get(name, None)
            if tool is None:
                raise KeyError(f'Tool with name "{name}" not found.')
            try:
                parsed_kwargs = json.loads(kwargs)
            except JSONDecodeError:
                raise ValueError(f"JSONDecodeError, could not parse JSON tools arguments {kwargs}.")
            tool_output: ToolOutput = tool(**parsed_kwargs)
        except Exception as ex:
            exception = str(ex)
            error_str = self.error_template.render(error=exception)
            meta = {"trace": traceback.format_exc(), "exception": exception}
            tool_output = ToolOutput(content=error_str, meta=meta)
        meta = {"tool_name": name, "tool_kwargs": kwargs, **tool_output.meta}
        return ToolOutputMsg(
            output=tool_output.content,
            call_id=tool_call.call_id,
            meta=meta,
        )
