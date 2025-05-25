from llmbrix.msg import MsgBase


class UserMsg(MsgBase):
    content: str
    role: str = "user"
