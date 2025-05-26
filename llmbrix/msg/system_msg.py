from llmbrix.base.msg_base import MsgBase


class SystemMsg(MsgBase):
    content: str
    role: str = "system"
