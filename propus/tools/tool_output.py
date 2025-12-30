from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ToolOutput(BaseModel):
    result: Any
    success: bool = True
    artifacts: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    debug_trace: Optional[Dict[str, Any]] = None
