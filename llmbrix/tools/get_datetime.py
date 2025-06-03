from datetime import datetime

from llmbrix.tool import Tool
from llmbrix.tool_output import ToolOutput

DATETIME_FMT = "%Y-%m-%d %H:%M:%S"
NAME = "get_current_datetime"
DESC = "Get current date and time in format {}."


class GetDatetime(Tool):
    """
    Get current datetime in str format.
    """

    def __init__(self, tool_name=NAME, tool_desc=DESC, datetime_fmt=DATETIME_FMT):
        """
        :param tool_name: str name of tool visible to LLM
        :param tool_desc: str description of tool visible to LLM.
                     Has to contain one format arg {} to fill the datetime format str.
        :param datetime_fmt: str datetime format, will be used to format output datetime
        """
        if "{}" not in tool_desc:
            raise ValueError("desc has to contain one format param {} to fill in datetime format str")
        tool_desc = tool_desc.format(datetime_fmt)
        self.datetime_fmt = datetime_fmt
        super().__init__(name=tool_name, desc=tool_desc)

    def exec(self) -> ToolOutput:
        """
        Get current datetime in str format.

        :return: ToolOutput object with str datetime as content.
        """
        return ToolOutput(content=datetime.now().strftime(self.datetime_fmt), meta={"datetime_fmt": self.datetime_fmt})
