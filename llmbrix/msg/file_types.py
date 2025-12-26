from enum import Enum


class FileTypes(Enum):
    """
    File types supported as an User input attachment.
    """

    # --- IMAGES ---
    IMAGE_PNG = "image/png"
    IMAGE_JPEG = "image/jpeg"

    # --- DOCUMENTS & DATA ---
    PDF = "application/pdf"
    PLAIN_TEXT = "text/plain"
    CSV = "text/csv"
    MARKDOWN = "text/md"
    JSON = "application/json"
    XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    # --- AUDIO ---
    AUDIO_MP3 = "audio/mp3"
    AUDIO_WAV = "audio/wav"

    # --- VIDEO ---
    VIDEO_MP4 = "video/mp4"
