import json
import os.path
import sys
from threading import Event

from PyQt6.QtCore import QObject, pyqtSignal, QThread, QMutex
from PyQt6.QtWidgets import QApplication

from log import logger
from src.py_qobject import PyQDict, PyQList, PyQObjectBase
from src.utils.type_cast import pyQDictToDictCopy


class WorkerThread(QThread):
    def __init__(self, _callable):
        super().__init__()
        self._callable = _callable

    def run(self):
        self._callable()
        self.finished.emit()


def getFilename(path: str) -> str:
    return os.path.basename(path)


class FileBase(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)


class JsonDataStorage(PyQObjectBase):
    def __init__(self, path: str, parent=None):
        super().__init__(parent)
        self._loaded = False
        self._loadEvent = Event()
        self._workerThread = None
        self._dict = PyQDict()
        self._dictLock = QMutex()
        self.path = path
        self.valueChanged.connect(self.dump)

    @property
    def dict(self) -> PyQDict:
        self._loadEvent.wait()
        return self._dict

    def dump(self):
        if self._workerThread is not None and self._workerThread.isRunning():
            logger.debug("wait for last dump thread to finish")
            self._workerThread.wait()
        self._workerThread = WorkerThread(self._dump)
        self._workerThread.start()

    def isLoaded(self) -> bool:
        return self._loaded

    def load(self):
        assert self._loaded is False
        self._loadEvent.clear()
        self._workerThread = WorkerThread(self._load)
        self._workerThread.start()

    def _dump(self) -> None:
        _dict = pyQDictToDictCopy(self._dict)
        with open(self.path, 'w') as f:
            json.dump(_dict, f, indent=4)
        logger.debug(f"Dumped data to {os.path.basename(self.path)}")
        self.dumped.emit()

    def _load(self) -> None:
        try:
            with open(self.path, "r") as f:
                _dict = json.load(f)
            self._dict = self._dictToPyQDict(_dict)
            self._dict.valueChanged.connect(self.valueChanged)
            self._loaded = True
            logger.debug(f"Loaded data from {os.path.basename(self.path)}")
        finally:
            self._loadEvent.set()
            self.loaded.emit()

    def _listToPyQList(self, _list: list) -> PyQList:
        res = PyQList()
        res.blockSignals(True)
        res.replaceList(_list)
        i = 0
        while i < len(res):
            cur = res[i]
            if isinstance(cur, dict):
                res[i] = self._dictToPyQDict(cur)
                res[i].valueChanged.connect(self.valueChanged)
            elif isinstance(cur, list):
                res[i] = self._listToPyQList(cur)
                res[i].valueChanged.connect(self.valueChanged)
            i += 1
        res.blockSignals(False)
        return res

    def _dictToPyQDict(self, _dict: dict) -> PyQDict:
        res = PyQDict()
        res.blockSignals(True)
        for k, v in _dict.items():
            if isinstance(v, dict):
                res[k] = self._dictToPyQDict(v)
                res[k].valueChanged.connect(self.valueChanged)
            elif isinstance(v, list):
                res[k] = self._listToPyQList(v)
                res[k].valueChanged.connect(self.valueChanged)
            else:
                res[k] = v
        res.blockSignals(False)
        return res

    loaded = pyqtSignal()
    dumped = pyqtSignal()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    _path = r"F:\one-more-thing\data\0b97bc434c154140b04d46f6ecf15d6f.json"
    storage = JsonDataStorage(_path)
    storage.load()
    storage.dict["name"] = "li si"
    sys.exit(app.exec())
