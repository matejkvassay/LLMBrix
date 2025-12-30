from typing import Any, Optional

from pydantic import BaseModel

from propus.tools.tool_param_types import ToolParamTypes


class ToolParam(BaseModel):
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
