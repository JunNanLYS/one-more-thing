import time

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy)
from qfluentwidgets import (SubtitleLabel, SegmentedToggleToolWidget, FluentIcon,
                            ToolButton, PopUpAniStackedWidget)

from log import logger
from src.do_thing_interface.project_edit_page import ProjectEditPageView


class T2(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vLayout = QVBoxLayout(self)
        self.vLayout.addWidget(SubtitleLabel("T2", self))
        self.vLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)


class DoThingInterface(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        logger.debug("---DoThingInterface initializing---")
        start = time.time()

        self.vLayout = QVBoxLayout(self)
        self.titleLb = SubtitleLabel("Do Thing", self)
        self.pivot = SegmentedToggleToolWidget(self)
        self.addBt = ToolButton(FluentIcon.ADD, self)
        self.updateBt = ToolButton(FluentIcon.UPDATE, self)
        self.view = PopUpAniStackedWidget(self)
        self.projectView = ProjectEditPageView(self.view, doThingBtCallback=self.tempSlot)

        self.__initWidget()
        logger.debug(f"Initialization time: {time.time() - start}")
        logger.debug("---DoThingInterface initialized---")

    # 占位用的槽函数
    def tempSlot(self, data):
        self.setCurrentIndex(1)
        self.pivot.setCurrentItem("time")

    def setCurrentIndex(self, index: int):
        if index == 0:
            self.addBt.show()
            self.updateBt.show()
            self.view.setCurrentIndex(0)
        elif index == 1:
            self.addBt.hide()
            self.updateBt.hide()
            self.view.setCurrentIndex(1)
        else:
            raise ValueError("Index out of range")

    def __initWidget(self):
        self.setObjectName("DoThingInterface")

        self.titleLb.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        self.view.addWidget(self.projectView, 0, -200)
        self.view.addWidget(T2(self), 0, 200)

        self.pivot.addItem("edit", FluentIcon.DATE_TIME, onClick=lambda: self.setCurrentIndex(0))
        self.pivot.addItem("time", FluentIcon.DATE_TIME, onClick=lambda: self.setCurrentIndex(1))
        self.pivot.setCurrentItem("edit")
        self.pivot.setFixedSize(self.pivot.size())

        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        toolLayout = QHBoxLayout()
        toolLayout.addWidget(self.pivot)
        toolLayout.addItem(QSpacerItem(0, 0, hPolicy=QSizePolicy.Policy.Expanding))
        toolLayout.addWidget(self.addBt)
        toolLayout.addWidget(self.updateBt)

        self.vLayout.addWidget(self.titleLb)
        self.vLayout.addLayout(toolLayout)
        self.vLayout.addWidget(self.view)
        self.vLayout.setContentsMargins(10, 10, 10, 10)
        self.vLayout.setSpacing(10)
        self.vLayout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

    def __connectSignalToSlot(self):
        pass
