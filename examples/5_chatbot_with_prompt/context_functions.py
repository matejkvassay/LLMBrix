from datetime import datetime
from time import time

RUN_START = time()


def get_current_weekday():
    weekday_name = datetime.now().strftime("%A")
    return {"weekday": weekday_name}


def get_uptime():
    dur = time() - RUN_START
    round(dur, 2)
    return {"uptime": dur}
