from llmbrix.msg.msg import Msg


class UserMsg(Msg):
    content: str
    role: str = "user"
