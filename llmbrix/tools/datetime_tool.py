from datetime import datetime

from propus.tool_calling.base_tool import BaseTool
from propus.tool_calling.tool_output import ToolOutput


class DatetimeTool(BaseTool):
    """
    Provides current system datetime information.
    """

    def __init__(self):
        super().__init__(
            name="get_current_datetime",
            description="Get current date and time (year, month, day, hour, minute, weekday, iso_format).",
        )

    def execute(self, **kwargs) -> ToolOutput:
        """
        Retrieves current datetime and returns a structured ToolOutput.
        """
        now = datetime.now()
        result_data = {
            "year": now.year,
            "month": now.month,
            "day": now.day,
            "hour": now.hour,
            "minute": now.minute,
            "weekday": now.strftime("%A"),
            "iso_format": now.isoformat(),
        }

        return ToolOutput(success=True, result=result_data, debug_trace={"engine": "python_datetime_module"})
