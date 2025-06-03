from typing import Union

ALLOWED_TYPES = Union[type[str], type[int], type[float], type[bool]]
PARAM_TYPE_MAP = {str: "string", int: "integer", bool: "boolean", float: "number"}


class ToolParam:
    """
    LLM-compatible tool parameter.
    """

    def __init__(self, name: str, desc: str, dtype: ALLOWED_TYPES, enum: list[ALLOWED_TYPES] = None):
        """
        :param name: str name of parameter visible to LLM. Has to be same as name of this parameter in
                     tool's exec() function.
        :param desc: str description of parameter visible to LLM.
        :param dtype: Type of parameter, has to be one of supported types.
        :param enum: (optional) List of allowed values for this parameter. Has to match the type from "dtype" param.
        """
        if dtype not in PARAM_TYPE_MAP:
            raise ValueError(f"Tool parameter type has to be one of: {PARAM_TYPE_MAP.keys()}")
        self.name = name
        self.desc = desc
        self.dtype = PARAM_TYPE_MAP[dtype]
        self.enum = enum

    @property
    def openai_schema(self) -> dict:
        """
        Formats this tool parameter to dict compatible with OpenAI responses API.

        :return: dict formatted for openAI responses API
        """
        properties_dict = {
            self.name: {
                "type": self.dtype,
                "description": self.desc,
            }
        }
        if self.enum is not None:
            properties_dict[self.name]["enum"] = [str(x) for x in self.enum]
        return properties_dict
