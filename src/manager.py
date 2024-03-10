import json
import os
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

from PyQt6.QtCore import QObject, pyqtSignal

import config as cfg
from log import logger
from src.source_data import SourceData


class SourceDataManager(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        logger.debug("---SourceDataManager initializing---")
        self._datas: list[SourceData] = []
        self.dataToPath: dict[SourceData, str] = {}
        self._loadLock = threading.Lock()

        self.load()
        logger.debug("---SourceDataManager initialized---")

    @property
    def datas(self) -> list[SourceData]:
        return self._datas

    def createData(self, name: str, icon: str, hours: float = 0.0) -> None:
        logger.debug(f"Create source data: {name}")
        uid = uuid.uuid4().hex
        dataFormat = cfg.defaultData
        dataFormat["name"] = name
        dataFormat["icon"] = icon
        dataFormat["hours"] = hours
        dataFormat["uid"] = uid
        path = os.path.join(cfg.dataPath, uid + ".json")
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
        start = time.time()
        logger.debug("Load source data from file system")
        filenames = os.listdir(cfg.dataPath)
        logger.info(f"Source data total quantity: {len(filenames)}")
        paths = [os.path.join(cfg.dataPath, filename) for filename in filenames]
        with ThreadPoolExecutor() as executor:
            executor.map(self.__load, paths)
        logger.info(f"Load source data time: {time.time() - start}")
        logger.debug("Source data loaded from file system")

    def reload(self) -> None:
        self._datas = []
        self.dataToPath = {}
        self.load()

    def __load(self, path: str) -> None:
        data = SourceData(path, self)
        with self._loadLock:
            self._datas.append(data)
            self.dataToPath[data] = path
        self.sourceDataCreated.emit(data)

    sourceDataCreated = pyqtSignal(SourceData)
    sourceDataDeleted = pyqtSignal(SourceData)


SDManager = SourceDataManager()
