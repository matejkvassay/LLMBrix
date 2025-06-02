from typing import Callable

from llmbrix.prompt import Prompt
from llmbrix.tool import Tool
from llmbrix.tool_output import ToolOutput

NAME = "get_info_about_me"
DESC = "Get information about this chatbot."


class AboutMe(Tool):
    """
    Provides information about this chatbot based on configured user info str or Prompt.
    """

    def __init__(self, info: str | Prompt, var_prep_func: Callable[[], dict] = None, tool_name=NAME, tool_desc=DESC):
        """
        :param info: str or Prompt containing description about chatbot to be returned to the user.
                         If prompt var_prep_func
        :param var_prep_func: function with no args, returning dict. This must be passed if "about_me" constructor
                              arg is Prompt type.
                              Function will be used with every tool execution to prepare dict of parameters
                              to be filled into the "about_me" prompt using prompt.render() function.
        :param tool_name: str name of tool visible to LLM
        :param tool_desc: str description of tool visible to LLM
        """
        if isinstance(info, Prompt):
            if var_prep_func is None:
                raise ValueError(
                    "If about_me is Prompt type you must pass function to build variables to the "
                    '"var_prep_func" constructor parameter'
                )
        self.info = info
        self.var_prep_func = var_prep_func

        super().__init__(name=tool_name, desc=tool_desc)

    def exec(self) -> ToolOutput:
        """
        Returns info about the chatbot.
        If "about_me" is str type its returned directly.
        If "about_me" is Prompt type, var_prep_func() is used to build variables dict and Prompt is rendered into str.

        :return: ToolOutput object containing info as content.
        """
        if isinstance(self.info, str):
            return ToolOutput(content=self.info, meta={"info_type": "str"})
        vars_ = self.var_prep_func()
        return ToolOutput(
            content=self.info.render(vars_), meta={"info_type": "Prompt", "info_prompt": str(self.info), "vars": vars_}
        )
