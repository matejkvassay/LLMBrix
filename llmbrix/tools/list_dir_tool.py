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
            desc="Return list of file names. Lists only files, not subdirs.",
            params=params,
        )

    @staticmethod
    def exec(dir_path: str):
        return [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
