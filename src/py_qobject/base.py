from PySide6.QtCore import QObject, Signal


class PyQObjectBase(QObject):
    valueChanged = Signal()
