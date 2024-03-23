import json
import os
import uuid
from typing import Union

from PyQt6.QtCore import QObject, pyqtSignal

import config as cfg
from log import logger
from src.py_qobject import PyQList, PyQDict
from src.source_data import SourceData
from src.utils.type_cast import pyQDictToDict


class SourceDataManager(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        logger.debug("---SourceDataManager initializing---")
        self.datas = PyQList(self)
        self.loadDatas()
        logger.debug("---SourceDataManager initialized---")

    def addData(self, name: str, icon: str):
        try:
            defaultData = cfg.getDefaultData()
            uid = defaultData["uid"]
            defaultData["name"] = name
            defaultData["icon"] = icon
            defaultData = pyQDictToDict(defaultData)
            with open(os.path.join(cfg.dataPath, f"{uid}.json"), "w") as f:
                json.dump(defaultData, f, indent=4)
            data = SourceData(os.path.join(cfg.dataPath, f"{uid}.json"))
            self.datas.append(data)
            self.dataAdded.emit(data)
        except Exception as e:
            logger.error(f"{e}")

    def findData(self, uid: str) -> Union[SourceData, None]:
        for data in self.datas:
            if data.storage.dict["uid"] == uid:
                return data
        return None

    def loadDatas(self):
        logger.debug("---Loading datas---")
        self.datas.blockSignals(True)
        filenames = os.listdir(cfg.dataPath)
        for filename in filenames:
            data = SourceData(os.path.join(cfg.dataPath, filename))
            self.datas.append(data)
        self.datas.blockSignals(False)
        logger.debug("---Data loaded---")

    def removeData(self, data: Union[SourceData, PyQDict]):
        if isinstance(data, PyQDict):
            data = self.findData(data["uid"])
        if data is None:
            logger.warning("removeData: Data not found")
            return
        os.remove(data.path)
        self.datas.remove(data)
        self.dataRemoved.emit(data)
        data.deleteLater()

    dataAdded = pyqtSignal(SourceData)
    dataRemoved = pyqtSignal(SourceData)


SDManager = SourceDataManager()
