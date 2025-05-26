from abc import ABC, abstractmethod

from llmbrix.tool_param import ToolParam


class Tool(ABC):
    def __init__(self, name: str, desc: str, params: tuple[ToolParam, ...] | None = None):
        self.name = name
        self.desc = desc
        self.params = params

    def __call__(self, **kwargs):
        return str(self.exec(**kwargs))

    @abstractmethod
    def exec(self, **kwargs):
        pass

    @property
    def openai_schema(self) -> dict:
        func_spec = {
            "name": self.name,
            "description": self.desc,
        }
        if self.params is not None:
            props = {}
            for param in self.params:
                props.update(param.openai_schema)
            func_spec["parameters"] = {
                "type": "object",
                "properties": props,
                "required": [x.name for x in self.params if x.required is True],
            }
        return {"type": "function", "function": func_spec}
