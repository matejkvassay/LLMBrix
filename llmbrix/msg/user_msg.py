from llmbrix.msg.msg import Msg


class UserMsg(Msg):
    """
    Message containing response from user.
    """

    content: str
    role: str = "user"
