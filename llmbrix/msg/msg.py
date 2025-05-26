from typing import Any, Optional

from pydantic import BaseModel


class Msg(BaseModel):
    role: str
    content: Optional[str] = None
    meta: Optional[dict[str, Any]] = None

    def to_openai(self) -> dict:
        return self.model_dump(exclude={"meta"})

    def __str__(self):
        content = self.content if self.content is not None else "<NO CONTENT>"
        return f'{self.role.upper()}: "{content}"'

    def __repr__(self):
        return self.__str__()
