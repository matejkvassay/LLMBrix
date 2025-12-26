from typing import Any, TypedDict

from llmbrix.msg.model_msg_segment_types import ModelMsgSegmentTypes


class ModelMsgSegment(TypedDict):
    type: ModelMsgSegmentTypes
    content: Any
    mime_type: str | None
