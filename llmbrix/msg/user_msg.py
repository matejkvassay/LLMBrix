from llmbrix.base.msg_base import MsgBase


class UserMsg(MsgBase):
    content: str
    role: str = "user"
