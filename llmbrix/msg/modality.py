from enum import Enum


class Modality(Enum):
    """
    File types supported by Gemini API.
    """

    # --- IMAGES ---
    IMAGE_PNG = "image/png"
    IMAGE_JPEG = "image/jpeg"
    IMAGE_WEBP = "image/webp"
    IMAGE_HEIC = "image/heic"
    IMAGE_HEIF = "image/heif"

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
    AUDIO_FLAC = "audio/flac"
    AUDIO_AAC = "audio/aac"
    AUDIO_OGG = "audio/ogg"

    # --- VIDEO ---
    VIDEO_MP4 = "video/mp4"
    VIDEO_MOV = "video/quicktime"
    VIDEO_WEBM = "video/webm"
    VIDEO_AVI = "video/x-msvideo"
