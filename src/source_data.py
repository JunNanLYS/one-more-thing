import json
import threading

from PyQt6.QtCore import pyqtSignal, QObject

from log import logger
from src.utils.file import getFilename


class SourceData(QObject):
    def __init__(self, path: str, parent=None):
        super().__init__(parent)
        self._loadEvent = threading.Event()
        self._isChanged = False
        self._dict = {}
        self.path = path
        self.filename = getFilename(path)

        threading.Thread(target=self.load).start()
        self.dataChanged.connect(lambda: self.setState(True))
        self.updateData.connect(self.update)

    @property
    def dict(self) -> dict:
        self._loadEvent.wait()
        return self._dict

    @property
    def isChanged(self) -> bool:
        return self._isChanged

    def setState(self, state: bool) -> None:
        self._isChanged = state

    def load(self) -> None:
        logger.debug(f"Load data from {self.filename}")
        self._loadEvent.clear()
        with open(self.path, "r") as f:
            self._dict = json.load(f)
        self._loadEvent.set()
        logger.debug(f"Data loaded from {self.filename}")

    def update(self) -> None:
        if not self._isChanged:
            return

        threading.Thread(target=self.__update).start()

    def __update(self) -> None:
        logger.debug(f"Update data to {self.filename}")
        with open(self.path, "w") as f:
            json.dump(self._dict, f, indent=4)
        self._isChanged = False
        logger.debug(f"Update data finished to {self.filename}")

    dataChanged = pyqtSignal()
    updateData = pyqtSignal()
