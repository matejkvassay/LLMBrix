from typing import List, Optional, Tuple

import PIL.Image
from google.genai import types

from llmbrix.msg.modality import Modality


class UserMsg:
    role = "user"

    def __init__(
        self,
        text: str,
        images: Optional[List[PIL.Image.Image]] = None,
        youtube_urls: Optional[List[str]] = None,
        files: Optional[List[Tuple[bytes, Modality]]] = None,
    ):
        self.text = text
        self.images = images or []
        self.youtube_urls = youtube_urls or []
        self.files = files or []

    def to_gemini(self) -> types.Content:
        parts = []
        for url in self.youtube_urls:
            parts.append(types.Part.from_uri(file_uri=url, mime_type="video/youtube"))

        for img in self.images:
            parts.append(types.Part.from_image(img))

        for file_bytes, modality in self.files:
            parts.append(types.Part.from_bytes(data=file_bytes, mime_type=modality.value))

        if self.text:
            parts.append(types.Part.from_text(text=self.text))

        return types.Content(role=self.role, parts=parts)
