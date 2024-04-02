from PySide6.QtCore import Signal

from .base import PyQObjectBase


class PyQSet(PyQObjectBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._set = set()

    def add(self, value):
        self._set.add(value)
        self.valueChanged.emit()
        self.elementAdded.emit(value)

    def clear(self):
        self._set.clear()
        self.valueChanged.emit()

    def remove(self, value):
        self._set.remove(value)
        self.valueChanged.emit()
        self.elementRemoved.emit(value)

    def __contains__(self, item):
        return self._set.__contains__(item)

    def __str__(self):
        return self._set.__str__()

    def __repr__(self):
        return self._set.__repr__()

    elementAdded = Signal(object)
    elementRemoved = Signal(object)
