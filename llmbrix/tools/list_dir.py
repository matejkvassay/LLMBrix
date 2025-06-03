import os

from llmbrix.tool import Tool
from llmbrix.tool_output import ToolOutput
from llmbrix.tool_param import ToolParam

NAME = "list_files_in_directory"
DESC = "List files in given directory."
PARAM_DESC = "Path to directory."


class ListDir(Tool):
    """
    Lists all files in given directory. Uses os.listdir().
    """

    def __init__(self, tool_name: str = NAME, tool_desc: str = DESC, tool_param_desc: str = PARAM_DESC):
        """
        :param tool_name: str, name of tool visible to LLM
        :param tool_desc: str, description of tool visible to LLM
        :param tool_param_desc: description for the tool "dir_path" parameter, visible to LLM
        """
        param = ToolParam(name="dir_path", desc=tool_param_desc, dtype=str)
        super().__init__(name=tool_name, desc=tool_desc, params=[param])

    @staticmethod
    def exec(dir_path: str) -> ToolOutput:
        """
        List files in given dir.

        :param dir_path: str path to dir to list files in
        :return: ToolOutput containing str of sorted list of file names as content.
        """
        return ToolOutput(content=str(sorted(os.listdir(dir_path))), meta={"dir_path": dir_path})
