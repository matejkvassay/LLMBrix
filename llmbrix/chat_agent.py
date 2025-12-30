from google.genai import Client

from llmbrix.msg import BaseMsg

DEFAULT_TOOL_EXECUTOR = None


class LlmAgent:
    def __init__(self, client: Client, model_name: str, tools=None, tool_executor=DEFAULT_TOOL_EXECUTOR):
        self.model_name = model_name
        self.client = Client()

    def chat(
        self,
        messages: list[BaseMsg],
    ):
        pass
