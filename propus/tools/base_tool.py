from abc import ABC, abstractmethod
from typing import Any, Dict, List

from google.genai import types

from propus.tools.tool_output import ToolOutput
from propus.tools.tool_param import ToolParam


class BaseTool(ABC, types.Tool):
    """
    Base class for implementation of tools compatible with Gemini API.
    """

    def __init__(self, name: str, description: str, params: List[ToolParam] | None = None, **kwargs):
        """
        Args:
            name: Name of LLM tool.
            description: Description of LLM tool.
            params: List of parameters. Note parameters need to exactly match your parameters
                    going into execute() method.
            **kwargs:
        """
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
    def execute(self, **kwargs) -> ToolOutput:
        """
        Tool execution logic to be implemented by a subclass.
        Note "context" parameter will always be passed by tool execution engine to enable contextualized execution.

        Args:
            **kwargs: Any kwargs specific for your tool (replace with named arguments).
                      They must 1:1 match parameters passed in "params" constructor argument.

        Returns:
            ToolOutput object.
        """
        raise NotImplementedError()
