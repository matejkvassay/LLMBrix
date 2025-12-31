from abc import ABC, abstractmethod
from typing import Any, Dict, List

from google.genai import types

from propus.tools.tool_param import ToolParam


class BaseTool(ABC, types.Tool):
    def __init__(self, name: str, description: str, params: List[ToolParam], **kwargs):
        properties: Dict[str, Any] = {param.name: param.to_json_dict() for param in params}
        required_params: List[str] = [param.name for param in params if param.required]
        func_declaration = types.FunctionDeclaration(
            name=name,
            description=description,
            parameters_json_schema={
                "type": "object",
                "properties": properties,
                "required": required_params,
            },
        )
        super().__init__(function_declarations=[func_declaration], **kwargs)

    @abstractmethod
    def execute(self, context: dict | None = None, **kwargs) -> dict:
        """
        Tool execution logic.
        """
        raise NotImplementedError()
