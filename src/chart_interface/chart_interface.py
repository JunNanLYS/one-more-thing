from PyQt6.QtWidgets import QWidget
from qfluentwidgets import TitleLabel


class ChartInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.label = TitleLabel("Chart", self)
        self.__initWidget()

    def __initWidget(self):
        self.setObjectName("ChartInterface")
        self.__initLayout()

    def __initLayout(self):
        self.label.move(36, 30)
