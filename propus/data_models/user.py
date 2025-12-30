from typing import Optional

from pydantic import BaseModel, Field


class User(BaseModel):
    id: str
    roles: Optional[list[str]] = Field(default_factory=list)
