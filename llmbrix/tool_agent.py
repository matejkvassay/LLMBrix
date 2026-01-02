from typing import Optional

import PIL.Image

from llmbrix.chat_history import ChatHistory
from llmbrix.gemini_model import GeminiModel
from llmbrix.msg import BaseMsg, UserMsg, UserMsgFileTypes
from llmbrix.tool_calling import BaseTool, ToolExecutor


class ToolAgent:
    """
    Tool calling agent. Can either act as a chatbot or single turn agent.
    """

    def __init__(
        self,
        gemini_model: GeminiModel,
        system_instruction: str,
        chat_history: Optional[ChatHistory] = None,
        tools: Optional[list[BaseTool]] = None,
        loop_limit: int = 3,
        tool_timeout: int = 120,
        max_workers: int = 4,
    ):
        self.gemini_model = gemini_model
        self.system_instruction = system_instruction
        self.chat_history = chat_history
        self.tool_executor = None
        if tools:
            self.tool_executor = ToolExecutor(tools=tools, max_workers=max_workers, timeout=tool_timeout)
        self.loop_limit = loop_limit

    def chat(
        self,
        text: str | list[BaseMsg],
        images: Optional[list[PIL.Image.Image]] = None,
        files: Optional[list[tuple[bytes, UserMsgFileTypes]]] = None,
        youtube_url: Optional[str] = None,
        gcs_uris: Optional[list[tuple[str, UserMsgFileTypes]]] = None,
    ):
        user_msg = UserMsg(text=text, images=images, files=files, youtube_url=youtube_url, gcs_uris=gcs_uris)
        if self.chat_history:
            messages = self.chat_history.get().append(user_msg)
        else:
            messages = [user_msg]
        model_msg = self.gemini_model.generate(messages, system_instruction=self.system_instruction)
        tool_iter = 1
        while model_msg.tool_calls and tool_iter <= self.loop_limit:
            self.tool_executor.execute(model_msg.tool_calls)

            tool_iter += 1
