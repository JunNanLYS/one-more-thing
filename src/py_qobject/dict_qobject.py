from copy import deepcopy

from .base import PyQObjectBase


class PyQDict(PyQObjectBase):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self._dict = dict(**kwargs)

    @property
    def dict(self):
        return self._dict

    def get(self, key, default=None):
        return self._dict.get(key, default)

    def items(self):
        return self._dict.items()

    def keys(self):
        return self._dict.keys()

    def pop(self, key):
        res = self._dict.pop(key)
        self.valueChanged.emit()
        return res

    def replaceDict(self, _dict: dict) -> None:
        self._dict = _dict
        self.valueChanged.emit()

    def values(self):
        return self._dict.values()

    def __contains__(self, item):
        return self._dict.__contains__(item)

    def __repr__(self):
        return self._dict.__repr__()

    def __str__(self):
        return f"PyQDict({self._dict})"

    def __setitem__(self, key, value):
        self._dict.__setitem__(key, value)
        self.valueChanged.emit()

    def __getitem__(self, key):
        return self._dict.__getitem__(key)

    def __delitem__(self, key):
        self._dict.__delitem__(key)
        self.valueChanged.emit()
