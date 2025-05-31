import pytest

from llmbrix.prompt import Prompt
from llmbrix.prompt_reader import PromptReader

VALID_YAML = """
text: |
  Hello! This is a test prompt.
"""

MISSING_TEXT_YAML = """
description: Just metadata, no actual prompt.
"""


@pytest.fixture
def tmp_prompt_dir(tmp_path):
    return tmp_path


def test_read_valid_prompt(tmp_prompt_dir):
    prompt_file = tmp_prompt_dir / "test_prompt.yaml"
    prompt_file.write_text(VALID_YAML)

    reader = PromptReader(prompt_dir=str(tmp_prompt_dir))
    prompt = reader.read("test_prompt")

    assert isinstance(prompt, Prompt)
    assert "Hello! This is a test prompt." in prompt.template_str


def test_missing_prompt_file(tmp_prompt_dir):
    reader = PromptReader(prompt_dir=str(tmp_prompt_dir))

    with pytest.raises(FileNotFoundError):
        reader.read("nonexistent_prompt")


@pytest.mark.parametrize("ext", [".yaml", ".yml", ".YAML", ".YML"])
def test_prompt_name_with_extension_is_rejected(tmp_prompt_dir, ext):
    reader = PromptReader(prompt_dir=str(tmp_prompt_dir))

    with pytest.raises(ValueError, match="without .* extension"):
        reader.read("badname" + ext)


def test_yaml_missing_text_field(tmp_prompt_dir):
    prompt_file = tmp_prompt_dir / "invalid_prompt.yaml"
    prompt_file.write_text(MISSING_TEXT_YAML)

    reader = PromptReader(prompt_dir=str(tmp_prompt_dir))

    with pytest.raises(ValueError, match='must contain "text"'):
        reader.read("invalid_prompt")
