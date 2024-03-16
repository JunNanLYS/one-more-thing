from PyQt6.QtCore import QObject, pyqtSignal


class PyQObjectBase(QObject):
    valueChanged = pyqtSignal()
