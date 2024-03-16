from copy import deepcopy

from PyQt6.QtCore import pyqtSignal

from .base import PyQObjectBase


class PyQList(PyQObjectBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._list = list()

    def append(self, obj):
        self._list.append(obj)
        self.valueChanged.emit()
        self.elementAppended.emit(obj)

    def clear(self):
        self._list.clear()
        self.valueChanged.emit()

    @property
    def list(self):
        return self._list

    def index(self, obj):
        return self._list.index(obj)

    def pop(self):
        res = self._list.pop()
        self.valueChanged.emit()
        self.elementRemoved.emit(res)

    def remove(self, obj):
        self._list.remove(obj)
        self.valueChanged.emit()
        self.elementRemoved.emit(obj)

    def replaceList(self, _list: list) -> None:
        self._list = _list
        self.valueChanged.emit()

    def __contains__(self, item):
        return self._list.__contains__(item)

    def __getitem__(self, item):
        return self._list.__getitem__(item)

    def __len__(self):
        return self._list.__len__()

    def __iter__(self):
        return self._list.__iter__()

    def __setitem__(self, key, value):
        self._list.__setitem__(key, value)
        self.valueChanged.emit()

    def __str__(self):
        return f"PyQList({self._list.__str__()})"

    def __repr__(self):
        return self._list.__repr__()

    elementAppended = pyqtSignal(object)
    elementRemoved = pyqtSignal(object)
