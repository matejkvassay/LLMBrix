from typing import Optional

import PIL.Image

from propus.gemini_model import GeminiModel
from propus.msg.user_msg_file_types import UserMsgFileTypes
from propus.tool_calling.base_tool import BaseTool
from propus.tool_calling.tool_executor import ToolExecutor


class ToolAgent:
    def __init__(
        self,
        gemini_model: GeminiModel,
        tools: Optional[list[BaseTool]] = None,
        loop_limit: int = 3,
        tool_timeout: int = 120,
        max_workers: int = 4,
    ):
        self.gemini_model = gemini_model
        self.tool_executor = None
        if tools:
            self.tool_executor = ToolExecutor(tools=tools, max_workers=max_workers, timeout=tool_timeout)
        self.loop_limit = loop_limit

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
