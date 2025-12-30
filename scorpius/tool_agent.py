from scorpius.gemini_model import GeminiModel


class ToolAgent:
    def __init__(self, gemini_model: GeminiModel, tools, tool_executor):
        self.gemini_model = gemini_model

    def chat(self):
        pass
