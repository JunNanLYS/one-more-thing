import json
import os
import threading
import uuid

from PyQt6.QtCore import QObject, pyqtSignal

import config as cfg
from log import logger
from src.source_data import SourceData

SOURCE_FILE_PATH = os.path.join(cfg.__abspath__, "data")


class SourceDataManager(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._datas: list[SourceData] = []
        self.dataToPath: dict[SourceData, str] = {}
        self._loadEvent = threading.Event()

        threading.Thread(target=self.load).start()

    @property
    def datas(self) -> list[SourceData]:
        self._loadEvent.wait()
        return self._datas

    def createData(self, name: str, icon: str, hours: float = 0.0) -> None:
        logger.debug(f"Create source data: {name}")
        uid = uuid.uuid4().hex
        dataFormat = cfg.defaultFormat
        dataFormat["name"] = name
        dataFormat["icon"] = icon
        dataFormat["hours"] = hours
        dataFormat["uid"] = uid
        path = os.path.join(SOURCE_FILE_PATH, uid + ".json")
        with open(path, 'w') as f:
            json.dump(dataFormat, f, indent=4)

        data = SourceData(path, self)
        self._datas.append(data)
        self.dataToPath[data] = path
        self.sourceDataCreated.emit(data)
        logger.debug(f"Source data created: {name}")

    def deleteData(self, data: SourceData) -> None:
        logger.debug(f"Delete data: {data.filename}")
        path = self.dataToPath[data]
        os.remove(path)
        self._datas.remove(data)
        self.dataToPath.pop(data)
        self.sourceDataDeleted.emit(data)
        logger.debug(f"Data deleted: {data.filename}")

    def load(self) -> None:
        logger.debug("Load source data from file system")
        self._loadEvent.clear()
        filenames = os.listdir(SOURCE_FILE_PATH)
        logger.info(f"Source data total quantity: {len(filenames)}")
        for filename in filenames:
            path = os.path.join(SOURCE_FILE_PATH, filename)
            data = SourceData(path, self)
            self._datas.append(data)
            self.dataToPath[data] = path
            self.sourceDataCreated.emit(data)
        self._loadEvent.set()
        logger.debug("Source data loaded from file system")

    def reload(self) -> None:
        self._datas = []
        self.dataToPath = {}
        self.load()

    # Reserve interface for future use
    def update(self) -> None:
        pass

    sourceDataCreated = pyqtSignal(SourceData)
    sourceDataDeleted = pyqtSignal(SourceData)


SDManager = SourceDataManager()
