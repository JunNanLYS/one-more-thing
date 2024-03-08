import json
import os.path
import threading
from abc import ABC, abstractmethod
from typing import Union

import config as cfg
from log import logger


def getFilename(path: str) -> str:
    for i in range(len(path) - 1, - 1, -1):
        if path[i] == "/" or path[i] == "\\":
            return path[i + 1:]
    return path


class File(ABC):
    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def update(self):
        pass


class JsonFile(File):
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.path = os.path.join(cfg.__abspath__, self.filename)
        self._data: Union[dict] = dict()
        self.loadEvent = threading.Event()

        threading.Thread(target=self.load).start()

    @property
    def data(self) -> Union[dict]:
        self.loadEvent.wait()
        return self._data

    # return the value of the key in the data attribute
    def getValue(self, keys: list[str]) -> None:
        self.loadEvent.wait()  # wait for the file to be loaded
        if isinstance(self._data, dict):
            res = self._data
            for key in keys:
                res = res[key]
            return res
        else:
            raise TypeError(f"the type of data attribute is {type(self._data)}")

    # read the file and store the data in the data attribute
    def load(self) -> None:
        logger.debug("loading json file")
        with open(self.path, 'r') as file:
            self._data = json.load(file)
        self.loadEvent.set()
        logger.debug("json file loaded")

    # set the value of the key in the data attribute
    def setValue(self, keys: list[str], value: Union[str, int, float, dict, list]) -> None:
        if isinstance(self._data, dict):
            key = keys.pop()
            data = self._data
            for k in keys:
                data = data[k]
            data[key] = value
        else:
            raise TypeError(f"the type of data attribute is {type(self._data)}")

    # write the data attribute to the file
    def update(self) -> None:
        with open(self.path, 'w') as file:
            json.dump(self._data, file, indent=4)


if __name__ == "__main__":
    p = r"F:\one-more-thing\data\0b97bc434c154140b04d46f6ecf15d6f.json"
    print(getFilename(p))
