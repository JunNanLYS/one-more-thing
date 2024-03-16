import sys

from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtWidgets import QApplication

from log import logger
from src.utils.file import JsonDataStorge


class SourceData(QObject):
    def __init__(self, path: str, parent=None):
        super().__init__(parent)
        self.path = path
        self._storge = JsonDataStorge(path)
        self._storge.dumped.connect(self.dumped)
        self._storge.loaded.connect(self.loaded)
        self._storge.load()

    def isLoaded(self) -> bool:
        return self._storge.isLoaded()

    @property
    def storge(self) -> JsonDataStorge:
        return self._storge

    dumped = pyqtSignal()
    loaded = pyqtSignal()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    _path = r"F:\one-more-thing\data\0b97bc434c154140b04d46f6ecf15d6f.json"
    d = SourceData(_path)
    d.loaded.connect(lambda: print("loaded"))
    logger.debug("我是主线程")
    d.storge.dict["name"] = "zhang san"
    app.exec()
