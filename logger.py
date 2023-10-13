import logging
from datetime import datetime
from pytz import timezone

def time_converter(*args):
    return datetime.now(tz=timezone('Asia/Shanghai')).timetuple()

logging.Formatter.converter = time_converter

logging.basicConfig(
    format="[%(asctime)s] %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

logging.basicConfig(
    filename='./error.log'
    format="[%(asctime)s] %(message)s",
    level=logging.ERROR,
    datefmt="%Y-%m-%d %H:%M:%S",
)
