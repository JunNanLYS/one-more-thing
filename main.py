import sys
import time

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

import config as cfg
from log import logger
from src.main import View as OneMoreThing
from src.utils import getScreenScale, getScreenSize

if __name__ == '__main__':
    screenWidth, screenHeight = getScreenSize()
    screenScale = getScreenScale()
    try:
        app = QApplication(sys.argv)
        if cfg.cfgDS.useOpenGL.value:
            app.setAttribute(Qt.ApplicationAttribute.AA_UseOpenGLES)
            logger.info("Enable hardware acceleration")
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
        logger.info(f"Application Start time: {time.time() - start}")
        app.exec()
        logger.debug("---Application exiting---\n")
        cfg.cfgDS.save()
    except Exception as e:
        logger.error(f"{e}")
        cfg.cfgDS.save()
    finally:
        sys.exit()
