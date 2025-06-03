from abc import ABC, abstractmethod

from llmbrix.tool_output import ToolOutput
from llmbrix.tool_param import ToolParam


class Tool(ABC):
    """
    Tool usable by LLM.
    """

    def __init__(self, name: str, desc: str, params: list[ToolParam] | None = None):
        """
        :param name: str name of tool visible to LLM
        :param desc: str desc of tool visible to LLM
        :param params: (optional) list of TopolParam objects representing parameters of tool. Parameter names must
                        exactly match parameters defined in "exec()" function.
        """
        self.name = name
        self.desc = desc
        self.params = params

    def __call__(self, **kwargs):
        return self.exec(**kwargs)

    @abstractmethod
    def exec(self, **kwargs) -> ToolOutput:
        """
        Exec function will be called to execute tool.
        It can be static or not, it can optionally contain arguments that will be used as kwargs.
        It has to return ToolOutput.
        """
        pass

    @property
    def openai_schema(self) -> dict:
        """
        Prepares dictionary representing tool compatible with OpenAI responses API.

        :return: Responses API compatible representation of this tool.
        """
        func_spec = {"type": "function", "name": self.name, "description": self.desc}
        if self.params is not None:
            props = {}
            for param in self.params:
                props.update(param.openai_schema)
            func_spec["parameters"] = {
                "type": "object",
                "properties": props,
                "required": [p.name for p in self.params],
                "additionalProperties": False,
            }
            func_spec["strict"] = True
        return func_spec
