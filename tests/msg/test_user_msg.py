import PIL.Image
import pytest

from llmbrix.msg.user_msg import UserMsg
from llmbrix.msg.user_msg_file_types import UserMsgFileTypes


def test_user_msg_basic_text_part():
    msg = UserMsg(text="Hello")
    assert len(msg.parts) == 1
    assert msg.parts[0].text == "Hello"


def test_user_msg_youtube_always_first():
    msg = UserMsg(text="What is this?", youtube_url="https://youtube.com/...")
    assert msg.parts[0].file_data.mime_type == "video/youtube"
    assert msg.parts[1].text == "What is this?"


def test_user_msg_gcs_uri_handling():
    msg = UserMsg(text="Read this", gcs_uris=[("gs://bucket/doc.pdf", UserMsgFileTypes.PDF)])
    assert msg.parts[0].file_data.file_uri == "gs://bucket/doc.pdf"
    assert msg.parts[0].file_data.mime_type == "application/pdf"


def test_user_msg_bytes_attachment():
    msg = UserMsg(text="Audio", files=[(b"raw_audio", UserMsgFileTypes.AUDIO_MP3)])
    assert msg.parts[0].inline_data.data == b"raw_audio"
    assert msg.parts[0].inline_data.mime_type == "audio/mpeg"


def test_user_msg_multiple_attachments_limit():
    img = PIL.Image.new("RGB", (1, 1))
    # 3 images + 2 GCS URIs + 1 YouTube = 6 (Limit is 5)
    with pytest.raises(ValueError, match="Maximum 5 file attachments allowed"):
        UserMsg(
            text="Too many",
            images=[img, img, img],
            gcs_uris=[("a", UserMsgFileTypes.PDF), ("b", UserMsgFileTypes.PDF)],
            youtube_url="url",
        )
