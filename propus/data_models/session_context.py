from typing import Optional

from pydantic import BaseModel

from propus.data_models.user import User


class SessionContext(BaseModel):
    user: Optional[User] = None
    debug_mode: bool = False
