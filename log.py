import os
import logging
from datetime import datetime

import config as cfg

time_ = datetime.now().strftime("%Y-%m-%d")
prefix = cfg.logPath
filename = os.path.join(prefix, f"{time_}.log")

# logging config
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] | %(name)s | %(asctime)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(filename),
        logging.StreamHandler()  # 添加一个StreamHandler来输出到终端
    ]
)

logger = logging.getLogger("one-more-thing")

if __name__ == "__main__":
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
