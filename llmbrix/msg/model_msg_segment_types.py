from enum import Enum


class ModelMsgSegmentTypes(Enum):
    """
    File types which can be returned by the Gemini model.
    """

    TEXT = "text"
    TOOL_CALL = "tool_call"
    IMAGE = "image"
    THOUGHT = "thought"
    AUDIO = "audio"
    UNSUPPORTED_FILE = "unsupported_file"
