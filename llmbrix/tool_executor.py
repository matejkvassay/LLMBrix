import json
from json import JSONDecodeError

from jinja2 import Template

from llmbrix.msg import ToolOutputMsg, ToolRequestMsg
from llmbrix.tool import Tool

DEFAULT_TOOL_ERROR_TEMPLATE = Template("Error during tool execution: {{error}}")


class ToolExecutor:
    def __init__(self, tools: list[Tool], error_template: Template = DEFAULT_TOOL_ERROR_TEMPLATE):
        self.tool_idx = {t.name: t for t in tools}
        self.error_template = error_template

    def __call__(self, tool_calls: list[ToolRequestMsg]) -> list[ToolOutputMsg]:
        return self.exec(tool_calls)

    def exec(self, tool_calls: list[ToolRequestMsg]) -> list[ToolOutputMsg]:
        return [self._execute_tool_call(req) for req in tool_calls]

    def _execute_tool_call(self, tool_call: ToolRequestMsg) -> ToolOutputMsg:
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
            content = tool(**parsed_kwargs)
        except Exception as ex:
            content = self.error_template.render(error=str(ex))
        return ToolOutputMsg(
            content=content,
            call_id=tool_call.call_id,
            meta={"tool_name": name, "tool_kwargs": kwargs},
        )
