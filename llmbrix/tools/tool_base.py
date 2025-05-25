from abc import abstractmethod
from functools import lru_cache

from llmbrix.base.api_compatible_base import ApiCompatibleBase
from llmbrix.tools.tool_param import ToolParam


class ToolBase(ApiCompatibleBase):
    def __init__(self, name: str, desc: str, params: tuple[ToolParam, ...] | None = None):
        self.name = name
        self.desc = desc
        self.params = params

    def __call__(self, **kwargs):
        return str(self.exec(**kwargs))

    @abstractmethod
    def exec(self, **kwargs):
        pass

    @lru_cache(maxsize=1)
    def api_dict(self):
        func_spec = {
            "name": self.name,
            "description": self.desc,
        }
        if self.params is not None:
            props = {}
            [props.update(par.api_dict()) for par in self.params]
            func_spec["parameters"] = {
                "type": "object",
                "properties": props,
                "required": [x.name for x in self.params if x.required is True],
            }
        return {"type": "function", "function": func_spec}
