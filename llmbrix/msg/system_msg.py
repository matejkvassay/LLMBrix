from llmbrix.msg.msg import Msg


class SystemMsg(Msg):
    content: str
    role: str = "system"
