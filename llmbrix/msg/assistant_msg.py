from typing import Optional

from llmbrix.msg.msg import Msg


class AssistantMsg(Msg):
    content: Optional[str] = None
    role: str = "assistant"
