from llmbrix.msg import MsgBase


class SystemMsg(MsgBase):
    content: str
    role: str = "system"
