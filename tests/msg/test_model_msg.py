from google.genai import types
from pydantic import BaseModel

from llmbrix.msg.model_msg import ModelMsg
from llmbrix.msg.model_msg_segment_types import ModelMsgSegmentTypes


def test_model_from_text_is_valid_role():
    msg = ModelMsg.from_text("test")
    assert msg.role == "model"


def test_model_text_concatenation():
    parts = [types.Part(text="Hello "), types.Part(text="world!")]
    msg = ModelMsg(parts=parts)
    assert msg.text == "Hello world!"


def test_model_thought_extraction():
    parts = [types.Part(thought=True, text="I should use a tool"), types.Part(text="Final answer")]
    msg = ModelMsg(parts=parts)
    assert msg.thought == "I should use a tool"
    assert msg.text == "Final answer"


def test_model_empty_thought_warning():
    parts = [types.Part(thought=True, text="")]
    msg = ModelMsg(parts=parts)
    assert len(msg.segments) == 0


def test_model_image_segment_metadata():
    parts = [types.Part(inline_data=types.Blob(data=b"fake_bits", mime_type="image/jpeg"))]
    msg = ModelMsg(parts=parts)
    assert msg.segments[0].type == ModelMsgSegmentTypes.IMAGE
    assert msg.segments[0].mime_type == "image/jpeg"


def test_model_unsupported_part_fallback():
    parts = [types.Part(video_metadata=types.VideoMetadata(fps=60))]
    msg = ModelMsg(parts=parts)
    assert msg.segments[0].type == ModelMsgSegmentTypes.UNSUPPORTED_PART


def test_model_msg_structured_output_validation():
    class TestSchema(BaseModel):
        answer: str
        confidence: float

    mock_parsed = TestSchema(answer="The capital is Paris", confidence=0.99)
    parts = [types.Part.from_text(text='{"answer": "Paris", "confidence": 0.99}')]
    msg = ModelMsg(parts=parts, parsed=mock_parsed)
    assert msg.parsed is not None
    assert isinstance(msg.parsed, BaseModel)
    assert msg.parsed.answer == "The capital is Paris"
    assert msg.parsed.confidence == 0.99
    dump = msg.model_dump()
    print(dump)
    assert dump["parsed"]["answer"] == "The capital is Paris"
