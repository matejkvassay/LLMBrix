import pytest

from llmbrix.exceptions import PromptRenderError
from llmbrix.prompt import Prompt


def test_render_success():
    prompt = Prompt(template_str="Hello {{ name }}, today is {{ day }}.")
    result = prompt.render({"name": "Alice", "day": "Monday"})
    assert result == "Hello Alice, today is Monday."


def test_render_missing_variable():
    prompt = Prompt(template_str="Hello {{ name }}, today is {{ day }}.")
    with pytest.raises(PromptRenderError, match=r"Missing required variables: \['day'\]"):
        prompt.render({"name": "Alice"})


def test_render_extra_variable():
    prompt = Prompt(template_str="Hello {{ name }}.")
    with pytest.raises(PromptRenderError, match=r"Unexpected variables: \['day'\]"):
        prompt.render({"name": "Alice", "day": "Monday"})


def test_render_missing_and_extra():
    prompt = Prompt(template_str="Hello {{ name }}.")
    with pytest.raises(PromptRenderError, match=r"Missing required variables: \['name'\]"):
        prompt.render({"day": "Monday"})


def test_partial_render_success():
    prompt = Prompt(template_str="Hello {{ name }}, today is {{ day }}.")
    partial = prompt.partial_render({"name": "Alice"})
    assert isinstance(partial, Prompt)
    assert partial.template_str == "Hello Alice, today is {{ day }}."


def test_partial_render_extra_variable():
    prompt = Prompt(template_str="Hello {{ name }}.")
    with pytest.raises(PromptRenderError, match=r"Unexpected variables: \['day'\]"):
        prompt.partial_render({"name": "Alice", "day": "Monday"})


def test_partial_render_all_variables():
    prompt = Prompt(template_str="Hello {{ name }}, today is {{ day }}.")
    partial = prompt.partial_render({"name": "Alice", "day": "Monday"})
    assert partial.template_str == "Hello Alice, today is Monday."


def test_partial_render_no_variables():
    prompt = Prompt(template_str="Hello {{ name }}.")
    partial = prompt.partial_render({})
    assert partial.template_str == "Hello {{ name }}."


def test_partial_render_with_control_structures():
    prompt = Prompt(template_str="{% if name %}Hello {{ name }}!{% endif %} Today is {{ day }}.")
    partial = prompt.partial_render({"day": "Monday"})
    assert "Hello" not in partial.template_str or "{{ name }}" not in partial.template_str
    assert "Today is Monday." in partial.template_str
