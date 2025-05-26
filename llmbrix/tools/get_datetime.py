from datetime import datetime

from llmbrix.tools import Tool


class GetDatetimeTool(Tool):
    def __init__(self):
        super().__init__(
            name="get_current_datetime",
            desc='returns current date and time in format "%Y-%m-%d %H:%M:%S"',
        )

    @staticmethod
    def exec():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
