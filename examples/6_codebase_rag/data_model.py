import uuid
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field


class CodeObject(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    meta: Dict[str, Any] = Field(default_factory=dict)


class FunctionArg(CodeObject):
    name: str
    typehint: Optional[str] = None
    default_value: Optional[str] = None
    param_kind: Literal["positional", "vararg", "kwarg", "keyword"]


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
    bases: List[str] = []
    docstring: Optional[str] = None
    source_code: Optional[str] = None
    body: List["ScriptBlock"] = []


class Import(CodeObject):
    kind: Literal["import"] = "import"
    module: Optional[str]  # e.g. "os" or "collections"
    names: List[str]  # e.g. ["path", "walk"]
    aliases: Dict[str, Optional[str]] = Field(default_factory=dict)  # e.g. {"path": "p", "walk": "w"}
    source_code: str


class Comment(CodeObject):
    kind: Literal["comment"] = "comment"
    comment_type: Literal["inline", "doc", "section"]
    text: str
    is_inline: bool = False
    commented_statement: Optional[str] = None


class Code(CodeObject):
    kind: Literal["code"] = "code"
    statement_type: Optional[str]  # for future filtering by some categories of code statements
    source_code: str
    inline_comments: List[str] = []


class ScriptBlock(CodeObject):
    parent_id: Optional[str] = None
    content: Union[Function, Class, Comment, Import, Code]
    lineno_start: int
    lineno_end: int


class PythonFile(CodeObject):
    language: Literal["python"] = "python"
    file_name: str
    path_rel: str
    path_abs: str
    docstring: Optional[str] = None
    blocks: List[ScriptBlock] = []


ScriptBlock.model_rebuild()
Function.model_rebuild()
Class.model_rebuild()
