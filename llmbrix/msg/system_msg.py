from llmbrix.msg.msg import Msg


class SystemMsg(Msg):
    """
    System message used as first message in the conversation to provide general instructions to
    the chatbot.
    """

    content: str
    role: str = "system"
