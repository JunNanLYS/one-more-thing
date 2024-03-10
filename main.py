import sys
import sys
import time

from PyQt6.QtWidgets import QApplication

import config as cfg
from log import logger
from src.main import View as OneMoreThing
from src.utils import getScreenScale, getScreenSize

if __name__ == '__main__':
    screenWidth, screenHeight = getScreenSize()
    screenScale = getScreenScale()
    app = QApplication(sys.argv)
    logger.info(f"Version: {cfg.__version__}")
    logger.info(f"Screen size: {screenWidth}*{screenHeight}, scale: {screenScale}")
    logger.debug("---Application initializing---")
    start = time.time()
    oneMoreThing = OneMoreThing()
    x = (screenWidth / 2) - (oneMoreThing.width() / 2)
    y = (screenHeight / 2) - (oneMoreThing.height() / 2)
    oneMoreThing.move(int(x), int(y))
    oneMoreThing.show()
    logger.debug("---Application Initialized---")
    logger.info(f"Start time: {time.time() - start}")
    app.exec()
    logger.debug("---Application exiting---\n")
    sys.exit()
