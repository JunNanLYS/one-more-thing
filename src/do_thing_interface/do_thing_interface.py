import time

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy)
from qfluentwidgets import (SubtitleLabel, SegmentedToggleToolWidget, FluentIcon,
                            PopUpAniStackedWidget, ToolButton, SwitchButton)

from log import logger
from src.do_thing_interface.choice_project_page import ChoiceProjectPage
from src.do_thing_interface.counter_page import CounterPage


class DoThingInterface(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        logger.debug("---DoThingInterface initializing---")
        start = time.time()

        self.vLayout = QVBoxLayout(self)
        self.titleLb = SubtitleLabel("Do Thing", self)
        self.pivot = SegmentedToggleToolWidget(self)
        self.view = PopUpAniStackedWidget(self)
        self.choicePage = ChoiceProjectPage(self)
        self.counterPage = CounterPage(self)
        self.countDownBt = SwitchButton(self)
        self.fullScreenBt = ToolButton(FluentIcon.FULL_SCREEN, self)

        self.__initWidget()
        logger.info(f"DoThingInterface Initialization time: {time.time() - start}")
        logger.debug("---DoThingInterface initialized---")

    # 占位用的槽函数
    def tempSlot(self, _dict):
        self.setCurrentIndex(1)
        self.pivot.setCurrentItem("time")

    def setCurrentIndex(self, index: int) -> None:
        if index == 0:
            self.fullScreenBt.hide()
            self.countDownBt.hide()
            self.view.setCurrentIndex(0)
        elif index == 1:
            self.fullScreenBt.show()
            self.countDownBt.show()
            self.view.setCurrentIndex(1)
        else:
            raise ValueError("Index out of range")

    def __connectSignalToSlot(self) -> None:
        self.choicePage.timeBtClicked.connect(self.tempSlot)
        self.fullScreenBt.clicked.connect(self.counterPage.fullScreen)
        self.countDownBt.checkedChanged.connect(self.counterPage.setCountDown)
        self.counterPage.modeChanged.connect(lambda mode: self.countDownBt.setEnabled(mode == "stop"))

    def __initWidget(self) -> None:
        self.setObjectName("DoThingInterface")

        self.titleLb.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        self.view.addWidget(self.choicePage, 0, -200)
        self.view.addWidget(self.counterPage, 0, 200)

        self.pivot.addItem("edit", FluentIcon.DATE_TIME, onClick=lambda: self.setCurrentIndex(0))
        self.pivot.addItem("time", FluentIcon.DATE_TIME, onClick=lambda: self.setCurrentIndex(1))
        self.pivot.setCurrentItem("edit")
        self.pivot.setFixedSize(self.pivot.size())

        self.countDownBt.setOffText("count up")
        self.countDownBt.setOnText("count down")
        self.fullScreenBt.hide()
        self.countDownBt.hide()

        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self) -> None:
        toolLayout = QHBoxLayout()
        toolLayout.addWidget(self.pivot)
        toolLayout.addItem(QSpacerItem(0, 0, hPolicy=QSizePolicy.Policy.Expanding))
        toolLayout.addWidget(self.countDownBt)
        toolLayout.addWidget(self.fullScreenBt)

        self.vLayout.addWidget(self.titleLb)
        self.vLayout.addLayout(toolLayout)
        self.vLayout.addWidget(self.view)
        self.vLayout.setContentsMargins(10, 10, 10, 10)
        self.vLayout.setSpacing(10)
        self.vLayout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
