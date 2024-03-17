import json
import os
import uuid

from PyQt6.QtCore import QObject, pyqtSignal

import config as cfg
from log import logger
from src.py_qobject import PyQList
from src.source_data import SourceData


class SourceDataManager(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        logger.debug("---SourceDataManager initializing---")
        self.datas = PyQList(self)
        self.loadDatas()
        logger.debug("---SourceDataManager initialized---")

    def addData(self, name: str, icon: str):
        uid = uuid.uuid4()
        defaultData = cfg.getDefaultData()
        defaultData["uid"] = uid
        defaultData["name"] = name
        defaultData["icon"] = icon
        with open(os.path.join(cfg.dataPath, f"{uid}.json"), "w") as f:
            json.dump(defaultData, f, indent=4)
        data = SourceData(os.path.join(cfg.dataPath, f"{uid}.json"))
        self.datas.append(data)
        self.dataAdded.emit(data)

    def loadDatas(self):
        logger.debug("---Loading datas---")
        self.datas.blockSignals(True)
        filenames = os.listdir(cfg.dataPath)
        for filename in filenames:
            self.datas.append(SourceData(os.path.join(cfg.dataPath, filename)))
        self.datas.blockSignals(False)
        logger.debug("---Data loaded---")

    def removeData(self, data: SourceData):
        os.remove(data.path)
        self.datas.remove(data)
        self.dataRemoved.emit(data)

    dataAdded = pyqtSignal(SourceData)
    dataRemoved = pyqtSignal(SourceData)


SDManager = SourceDataManager()
