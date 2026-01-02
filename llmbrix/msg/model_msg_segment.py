from dataclasses import dataclass
from typing import Any

from propus.msg.model_msg_segment_types import ModelMsgSegmentTypes


@dataclass
class ModelMsgSegment:
    type: ModelMsgSegmentTypes
    content: Any
    mime_type: str | None
