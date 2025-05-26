import os

from llmbrix.tool import Tool
from llmbrix.tool_param import ToolParam


class ListDirTool(Tool):
    def __init__(self):
        params = [
            ToolParam(name="dir_path", desc="Path to directory to list files from.", dtype=str)
        ]
        super().__init__(
            name="list_files_in_directory",
            desc="Return list of file names. Lists both files and sub-dirs.",
            params=params,
        )

    @staticmethod
    def exec(dir_path: str):
        return os.listdir(dir_path)
