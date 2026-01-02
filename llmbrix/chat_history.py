from llmbrix.msg import BaseMsg


class ChatHistory:
    def __init__(self):
        pass

    def get(self, n=None):
        pass

    def insert(self, messages=BaseMsg | list[BaseMsg]):
        if isinstance(messages, BaseMsg):
            messages = [messages]
