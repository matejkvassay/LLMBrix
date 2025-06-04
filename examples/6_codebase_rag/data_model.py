from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field


class CodeObject(BaseModel):
    meta: Dict[str, Any] = Field(default_factory=dict)


class Constant(CodeObject):
    name: str
    value_repr: str  # str representation of python statement that is defined as value to this constant


class FunctionArg(CodeObject):
    name: str
    typehint: Optional[str] = None
    default_value: Optional[str] = None


class Function(CodeObject):
    kind: Literal["function"] = "function"
    decorators: List[str] = []
    name: str
    args: List[FunctionArg] = []
    return_typehint: Optional[str] = None
    docstring: Optional[str] = None
    source_code: Optional[str] = None
    body: List["ScriptBlock"] = []


class Class(CodeObject):
    kind: Literal["class"] = "class"
    name: str
    base_classes: List[str] = []
    docstring: Optional[str] = None
    class_vars: List[Constant] = []
    source_code: Optional[str] = None
    body: List["ScriptBlock"] = []


class Code(CodeObject):
    kind: Literal["code"] = "code"
    source_code: str
    inline_comments: List[str] = []


class Comment(CodeObject):
    kind: Literal["comment"] = "comment"
    text: str
    is_inline: bool = False
    commented_statement: Optional[str] = None


class ScriptBlock(CodeObject):
    content: Union[Function, Class, Code, Comment]
    lineno_start: int
    lineno_end: int


class PythonFile(CodeObject):
    file_name: str
    path_rel: str
    path_abs: str
    docstring: Optional[str] = None
    blocks: List[ScriptBlock] = []


Function.model_rebuild()
Class.model_rebuild()
