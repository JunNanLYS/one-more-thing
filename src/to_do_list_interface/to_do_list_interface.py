from PySide6.QtCore import QEasingCurve, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (TitleLabel, SmoothScrollArea, SimpleCardWidget,
                            CheckBox, SubtitleLabel, ToolButton, FluentIcon)

from src.utils import getLabelBoundingRect


class ToDoItem(SimpleCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hLayout = QHBoxLayout(self)
        self.checkBox = CheckBox(self)
        self.info = SubtitleLabel("This is a to do item", self)
        self.__initWidget()

    def onStateChanged(self, state: bool):
        styleSheet = self.info.styleSheet()
        if state:
            self.info.setStyleSheet(styleSheet + "QLabel {text-decoration: line-through;}")
        else:
            self.info.setStyleSheet(styleSheet + "QLabel {text-decoration: none;}")

    def __connectSignalToSlot(self):
        self.checkBox.stateChanged.connect(self.onStateChanged)

    def __initWidget(self):
        self.checkBox.setFixedSize(20, 20)
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.hLayout.addWidget(self.checkBox)
        self.hLayout.addWidget(self.info, 1)
        self.hLayout.setContentsMargins(20, 20, 20, 20)
        self.hLayout.setSpacing(10)
        self.hLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)


class ToDoListInterface(SmoothScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.view = QWidget(self)
        self.vLayout = QVBoxLayout(self.view)
        self.mainLayout = QVBoxLayout(self)
        self.titleLb = TitleLabel("To do list", self)
        self._setQss()
        self.__initWidget()

    def _setQss(self):
        self.setStyleSheet("QScrollArea{background: transparent; border: none;}")
        self.view.setStyleSheet("QWidget{background: transparent}")

    def __connectSignalToSlot(self):
        pass

    def __initWidget(self):
        self.setObjectName("ToDoListInterface")
        rect = getLabelBoundingRect(self.titleLb)
        self.titleLb.setFixedSize(rect.width(), rect.height())
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.setViewportMargins(0, 80, 0, 20)
        self.setScrollAnimation(Qt.Orientation.Vertical, 400, QEasingCurve.OutQuint)
        self.setScrollAnimation(Qt.Orientation.Horizontal, 400, QEasingCurve.OutQuint)
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.titleLb.move(36, 30)

        for _ in range(20):
            toDoItem = ToDoItem(self.view)
            self.vLayout.addWidget(toDoItem)

        self.vLayout.setSpacing(10)
        self.vLayout.setContentsMargins(36, 10, 36, 0)
        self.mainLayout.addWidget(ToolButton(FluentIcon.ADD, self))
        self.mainLayout.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        self.mainLayout.setContentsMargins(36, 30, 36, 30)
