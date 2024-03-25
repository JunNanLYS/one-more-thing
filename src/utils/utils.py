from PySide6.QtCore import QRect, Qt
from PySide6.QtWidgets import QLabel

from log import logger
from src.py_qobject import PyQDict, PyQList


def getLabelBoundingRect(label: QLabel) -> QRect:
    return label.fontMetrics().boundingRect(label.text())


def addSubItem(_dict: PyQDict, item: PyQDict) -> bool:
    try:
        _list: PyQList = _dict["subItems"]
        _list.append(item)
        item.valueChanged.connect(_list.valueChanged.emit, Qt.ConnectionType.UniqueConnection)
        return True
    except Exception as e:
        logger.error(f"{e}")
        return False


def removeSubItem(_dict: PyQDict, item: PyQDict) -> bool:
    try:
        _list = _dict["subItems"]
        _list.remove(item)
        item.deleteLater()
        return True
    except Exception as e:
        logger.error(f"{e}")
        return False
