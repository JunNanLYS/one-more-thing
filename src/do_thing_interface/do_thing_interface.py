import time

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QFrame, QVBoxLayout)
from qfluentwidgets import (PopUpAniStackedWidget, TitleLabel)

from log import logger
from src.do_thing_interface.choice_project_page import ChoiceProjectPage
from src.do_thing_interface.counter_page import CounterPage


class DoThingInterface(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        logger.debug("---DoThingInterface initializing---")
        start = time.time()

        self.vLayout = QVBoxLayout(self)
        self.titleLb = TitleLabel("Do Thing", self)
        self.view = PopUpAniStackedWidget(self)
        self.choicePage = ChoiceProjectPage(self)
        self.counterPage = CounterPage(self)

        self.__initWidget()
        logger.info(f"DoThingInterface Initialization time: {time.time() - start}")
        logger.debug("---DoThingInterface initialized---")

    # 占位用的槽函数
    def setCounterItem(self, _dict):
        self.setCurrentIndex(1)
        self.counterPage.setDict(_dict)

    def setCurrentIndex(self, index: int) -> None:
        if index == 0:
            self.view.setCurrentIndex(0)
        elif index == 1:
            self.view.setCurrentIndex(1)

    def __connectSignalToSlot(self) -> None:
        self.choicePage.timeBtClicked.connect(self.setCounterItem)
        self.counterPage.backBt.clicked.connect(lambda: self.setCurrentIndex(0))

    def __initWidget(self) -> None:
        self.setObjectName("DoThingInterface")
        # 获取字体像素大小
        rect = self.titleLb.fontMetrics().boundingRect(self.titleLb.text())
        self.titleLb.setFixedSize(rect.width() + 10, rect.height())
        self.view.addWidget(self.choicePage, 0, -200)
        self.view.addWidget(self.counterPage, 0, 200)

        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self) -> None:
        self.titleLb.move(36, 30)
        self.vLayout.addWidget(self.view)
        self.vLayout.setContentsMargins(36, 90, 36, 10)
        self.vLayout.setSpacing(10)
        self.vLayout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
