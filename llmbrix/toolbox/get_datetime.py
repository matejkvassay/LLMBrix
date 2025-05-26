from datetime import datetime

from llmbrix.tool import Tool


class GetDatetime(Tool):
    def __init__(self):
        super().__init__(
            name="get_current_datetime",
            desc='returns current date and time in format "%Y-%m-%d %H:%M:%S"',
        )

    @staticmethod
    def exec():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
