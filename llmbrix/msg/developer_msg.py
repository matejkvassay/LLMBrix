from llmbrix.msg.msg import Msg


class DeveloperMsg(Msg):
    content: str
    role: str = "developer"
