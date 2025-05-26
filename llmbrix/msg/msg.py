from typing import Any, Optional

from pydantic import BaseModel


class Msg(BaseModel):
    meta: Optional[dict[str, Any]] = None

    def to_openai(self) -> dict:
        exclude = ["meta"]
        return self.model_dump(exclude=set(exclude))
