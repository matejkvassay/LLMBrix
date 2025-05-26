from typing import Optional

from pydantic import BaseModel

from llmbrix.base.api_compatible_base import ApiCompatibleBase


class MsgBase(BaseModel, ApiCompatibleBase):
    role: str
    content: Optional[str] = None

    def __init__(self, content: Optional[str] = None, **kwargs):
        if content and "content" not in kwargs:
            kwargs["content"] = content
        super().__init__(**kwargs)

    def api_dict(self) -> dict:
        return self.dict()

    def __str__(self):
        content = self.content if self.content is not None else "<no content>"
        return f'{self.role.upper()}: "{content}"'

    def __repr__(self):
        return self.__str__()
