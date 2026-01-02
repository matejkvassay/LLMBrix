from typing import Any, Optional

from propus.tool_calling.tool_param_types import ToolParamTypes
from pydantic import BaseModel


class ToolParam(BaseModel):
    """
    Parameter of an LLM tool.
    Declares a tool parameter for the LLM.
    All following fields visible are seen by the LLM.
    """

    name: str  # has to be the same as name of parameter in your tool .execute() method
    description: str
    type: ToolParamTypes
    items_type: Optional[ToolParamTypes] = None  # only fill if param type == ToolParamTypes.ARRAY
    required: bool = True

    def to_json_dict(self):
        """
        Converts the param to a JSON Schema property.
        """
        schema: dict[str, Any] = {
            "type": self.type.value,
            "description": self.description,
        }
        if self.type == ToolParamTypes.ARRAY and self.items_type:
            schema["items"] = {"type": self.items_type.value}
        return schema
