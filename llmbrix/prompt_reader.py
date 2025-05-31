import os

import structlog
import yaml

from llmbrix.prompt import Prompt

logger = structlog.getLogger(__name__)


class PromptReader:
    """
    Simple reader of prompts from .yaml files.

    Yaml file has to end with .yaml extension and contain "text" field
    with prompt text as multiline str value.
    """

    def __init__(self, prompt_dir: str):
        """
        :param prompt_dir: str root dir where prompts / subdirs containing prompts are placed
        """
        self.prompt_dir = prompt_dir

    def read(self, prompt_name: str) -> Prompt:
        """
        Read prompt from .yaml file.
        The file is expected to end with .yaml extension (not .yml, not .YAML, not .YML).
        The .yaml extension it's automatically appended to the prompt_name passed in argument.

        :param prompt_name: Name of prompt file (without .yaml extension).
        :return: Prompt instance
        """
        if prompt_name.lower().endswith((".yaml", ".yml")):
            raise ValueError("Pass prompt file name without .yaml extension.")
        prompt_path = os.path.join(self.prompt_dir, prompt_name + ".yaml")
        logger.info("Reading prompt.", prompt_path=prompt_path)
        if not os.path.isfile(prompt_path):
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        with open(prompt_path, "r") as f:
            data = yaml.safe_load(f)
        if "text" not in data:
            raise ValueError('Prompt YAML must contain "text" field.')
        return Prompt(template_str=data["text"])
