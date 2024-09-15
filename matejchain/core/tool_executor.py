import json
import logging
from json import JSONDecodeError

from jinja2 import Template
from openai.types.chat import ChatCompletionMessageToolCall

from matejchain.base import ToolBase
from matejchain.msg import ToolMsg

logger = logging.getLogger(__name__)

DEFAULT_TOOL_ERROR_CONTENT = Template("Error during tool execution: {{error}}")


class ToolExecutor:
    def __init__(
        self, tools: list[ToolBase], error_template: Template = DEFAULT_TOOL_ERROR_CONTENT
    ):
        """

        :param tools: list of potential tools to execute
        :param error_template: Jinja2 template, optionally can to contain {{error}} var.
                            When error occurs during tool execution str error message will be
                            inserted into {{error}} variable of this template and returned
                            as content in ToolMsg.

        """
        self.tool_idx = {t.name: t for t in tools}
        self.error_template = error_template

    def exec(self, tool_calls: list[ChatCompletionMessageToolCall]):
        return [self._execute_tool_call(req) for req in tool_calls]

    def _execute_tool_call(self, tool_call: ChatCompletionMessageToolCall) -> ToolMsg:
        name = tool_call.function.name
        kwargs = tool_call.function.arguments
        try:
            tool = self.tool_idx.get(name, None)
            if tool is None:
                raise KeyError(f'Tool function with name "{name}" not found.')
            try:
                kwargs = json.loads(kwargs)
            except JSONDecodeError:
                raise ValueError(f"JSONDecodeError, could not parse JSON tool arguments {kwargs}.")
            tool_output = tool(**kwargs)
            return ToolMsg(content=tool_output, tool_call_id=tool_call.id)
        except Exception as ex:
            logger.exception(f"Tool call execution failed for req {tool_call.dict()}, error: {ex}")
            content = self.error_template.render(error=str(ex))
            return ToolMsg(content=content, tool_call_id=tool_call.id)
