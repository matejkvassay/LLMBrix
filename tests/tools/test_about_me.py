import pytest

from llmbrix.exceptions import PromptRenderError
from llmbrix.prompt import Prompt
from llmbrix.tools import AboutMe


def test_about_me_with_string():
    tool = AboutMe(info="I am a helpful chatbot.")
    assert tool.exec().content == "I am a helpful chatbot."


def test_about_me_with_prompt():
    info = Prompt("I'm your assistant, {{chatbot_name}}.")
    tool = AboutMe(info=info, var_prep_func=lambda: {"chatbot_name": "Kevin"})
    assert tool.exec().content == "I'm your assistant, Kevin."


def test_about_me_missing_var_fill_func():
    info = Prompt("I'm your assistant, {{chatbot_name}}.")
    with pytest.raises(ValueError):
        AboutMe(info=info)


def test_about_me_render_error():
    info = Prompt("I'm your assistant, {{chatbot_name}}.")
    tool = AboutMe(info=info, var_prep_func=lambda: {"name": "Kevin"})
    with pytest.raises(PromptRenderError):
        tool.exec()
