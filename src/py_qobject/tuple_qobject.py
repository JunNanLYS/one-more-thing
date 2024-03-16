from .base import PyQObjectBase


class PyQTuple(PyQObjectBase):
    def __init__(self, *elements, parent=None):
        super().__init__(parent)
        self._tuple = elements

    def count(self, value):
        return self._tuple.count(value)

    def index(self, value, start=0, stop=None):
        return self._tuple.index(value, start, stop)

    def __contains__(self, item):
        return self._tuple.__contains__(item)

    def __getitem__(self, item):
        return self._tuple.__getitem__(item)

    def __len__(self):
        return self._tuple.__len__()

    def __iter__(self):
        return self._tuple.__iter__()

    def __str__(self):
        return self._tuple.__str__()

    def __repr__(self):
        return self._tuple.__repr__()


