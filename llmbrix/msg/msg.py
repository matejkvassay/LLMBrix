from typing import Any, Optional

from pydantic import BaseModel


class Msg(BaseModel):
    role: str
    content: Optional[str] = None
    meta: Optional[dict[Any]] = None

    def __init__(self, content: Optional[str] = None, **kwargs):
        if content and "content" not in kwargs:
            kwargs["content"] = content
        super().__init__(**kwargs)

    def to_openai(self) -> dict:
        return self.model_dump(
            exclude={
                "meta",
            }
        )

    def __str__(self):
        content = self.content if self.content is not None else "<no content>"
        return f'{self.role.upper()}: "{content}"'

    def __repr__(self):
        return self.__str__()
