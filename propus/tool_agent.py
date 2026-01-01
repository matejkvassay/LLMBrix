from typing import Optional

import PIL.Image

from propus.gemini_model import GeminiModel
from propus.msg.user_msg_file_types import UserMsgFileTypes
from propus.tools.base_tool import BaseTool


class ToolAgent:
    def __init__(self, gemini_model: GeminiModel, tools: Optional[list[BaseTool]] = None, max_iterations: int = 3):
        self.gemini_model = gemini_model
        self.tools = tools
        self.max_iterations = max_iterations

    def chat(
        self,
        text: str,
        images: Optional[list[PIL.Image.Image]] = None,
        files: Optional[list[tuple[bytes, UserMsgFileTypes]]] = None,
        youtube_url: Optional[str] = None,
        gcs_uris: Optional[list[tuple[str, UserMsgFileTypes]]] = None,
    ):
        # user_msg = UserMsg(text=text, images=images, files=files, youtube_url=youtube_url, gcs_uris=gcs_uris)
        raise NotImplementedError()
