from enum import Enum


class UserMsgFileTypes(Enum):
    """
    File types supported as a User input attachment.
    """

    # --- IMAGES ---
    IMAGE_PNG = "image/png"
    IMAGE_JPEG = "image/jpeg"

    # --- DOCUMENTS & DATA ---
    PDF = "application/pdf"
    PLAIN_TEXT = "text/plain"

    # --- AUDIO ---
    AUDIO_MP3 = "audio/mpeg"
    AUDIO_WAV = "audio/wav"
