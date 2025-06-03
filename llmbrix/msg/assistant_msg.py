from typing import Optional

from llmbrix.msg.msg import Msg


class AssistantMsg(Msg):
    """
    Message containing response form LLM assistant.
    """

    content: Optional[str] = None
    role: str = "assistant"
