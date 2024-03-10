from typing import Union

from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLayoutItem, QWidget, QBoxLayout
from qfluentwidgets import SimpleCardWidget


class CardLayout(SimpleCardWidget):
    def __init__(self, vertical=False, parent=None):
        super().__init__(parent)
        if vertical:
            self._layout = QVBoxLayout(self)
        else:
            self._layout = QHBoxLayout(self)

    def layout(self) -> Union[QVBoxLayout, QHBoxLayout]:
        return self._layout

    def addWidget(self, widget: QWidget):
        self._layout.addWidget(widget)

    def addLayout(self, layout: Union[QVBoxLayout, QHBoxLayout]):
        self._layout.addLayout(layout)

    def addItem(self, item: QLayoutItem):
        self._layout.addItem(item)
