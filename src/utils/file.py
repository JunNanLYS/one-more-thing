import json
import os.path
import threading
from abc import ABC, abstractmethod, ABCMeta
from typing import Union

from PyQt6.QtCore import QObject
from PyQt6.sip import wrappertype

import config as cfg
from log import logger


def getFilename(path: str) -> str:
    return os.path.basename(path)


class FileBase(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)


if __name__ == "__main__":
    p = r"F:\one-more-thing\data\0b97bc434c154140b04d46f6ecf15d6f.json"
    print(os.path.basename(p))
