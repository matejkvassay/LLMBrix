from enum import Enum


class SegmentTypes(Enum):
    """
    File types which can be returned by the Gemini model.
    """

    TEXT = "text"
    TOOL_CALL = "tool_call"
    IMAGE = "image"
    FILE = "file"
    THOUGHT = "thought"
    AUDIO = "audio"
