import json
import os
import time
from typing import Optional
from uuid import uuid4

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy
from qfluentwidgets import (BreadcrumbBar, SegmentedToggleToolWidget, FluentIcon,
                            LineEdit, TitleLabel, SwitchButton, SubtitleLabel,
                            PushButton, FluentIconBase, ToolButton, StateToolTip)
from qfluentwidgets.window.stacked_widget import StackedWidget

import config as cfg
from log import logger
from src.do_thing_interface.icon_libraries import FluentIconLibrary, CustomIconLibrary
from src.do_thing_interface.project_view import ProjectView
from src.do_thing_interface.time_item_card import CardData
from src.manager import SDManager


class ViewPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.__mainLayout = QVBoxLayout(self)
        self.breadcrumb = BreadcrumbBar(self)
        self.view: Optional[ProjectView] = None
        self.updateBt = ToolButton(FluentIcon.UPDATE, self)

        self.__initWidget()
        logger.debug("ViewPage is ok")

    def __toolBtSlot(self):
        logger.debug("Update button clicked")
        tip = StateToolTip("Update", "Update all project", self.window())
        tip.move(tip.getSuitablePos())
        tip.show()
        pass

    def __connectSignalToSlot(self):
        self.updateBt.clicked.connect(self.__toolBtSlot)
        self.breadcrumb.currentItemChanged.connect(self.view.setCurrentPage)
        self.view.updateBreadcrumb.connect(self.breadcrumb.addItem)

    def __initWidget(self):
        self.breadcrumb.addItem("Root", "Root")

        # set breadcrumb font pixel size
        font = self.breadcrumb.font()
        font.setPixelSize(20)
        self.breadcrumb.setFont(font)

        # init
        self.view = ProjectView(self)

        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        toolLayout = QHBoxLayout()

        # add tool button to layout
        toolLayout.addItem(QSpacerItem(0, 0, hPolicy=QSizePolicy.Policy.Expanding))
        toolLayout.addWidget(self.updateBt)

        mainLayout = self.__mainLayout
        mainLayout.addWidget(self.breadcrumb)
        mainLayout.addLayout(toolLayout)
        mainLayout.addWidget(self.view)
        mainLayout.setContentsMargins(10, 10, 10, 10)
        mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)


class AddCardPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.__mainLayout = QVBoxLayout(self)

        self.titleLabel = TitleLabel(self)
        self.nameEditLabel = SubtitleLabel(self)
        self.nameEdit = LineEdit(self)
        self.iconLabel = SubtitleLabel(self)
        self.switchBt = SwitchButton(self)
        self.iconView = StackedWidget(self)
        self.fluentIL = FluentIconLibrary(self)
        self.CustomIL = CustomIconLibrary(self)
        self.confirmBt = PushButton("Confirm", self)
        self.cancelBt = PushButton("Cancel", self)

        self.__initWidget()
        logger.debug("AddCardPage is ok")

    def clearInput(self):
        self.nameEdit.clear()
        self.iconView.currentWidget().disSelect()

    def setCurrentIL(self):
        if self.switchBt.isChecked():
            self.iconView.setCurrentIndex(1)
        else:
            self.iconView.setCurrentIndex(0)
        self.iconView.currentWidget().disSelect()

    def __connectSignalToSlot(self):
        self.switchBt.checkedChanged.connect(self.setCurrentIL)
        self.confirmBt.clicked.connect(self.__confirmBtSlot)
        self.cancelBt.clicked.connect(self.__cancelBtSlot)

    def __confirmBtSlot(self):
        logger.debug("Confirm button clicked")
        name = self.nameEdit.text()
        icon: Optional[str, FluentIconBase] = self.iconView.currentWidget().getSelectedIcon()
        if isinstance(icon, FluentIcon):
            icon = "F-" + icon.name

        SDManager.createData(name, icon)
        self.clearInput()

    def __cancelBtSlot(self):
        logger.debug("Cancel button clicked")
        self.clearInput()

    def __initWidget(self):
        # set label text
        self.titleLabel.setText("Add new project")
        self.nameEditLabel.setText("Project name: ")
        self.iconLabel.setText("Set project icon: ")

        # set switch button text
        self.switchBt.setOffText("Fluent")
        self.switchBt.setOnText("Custom")

        # set editLine
        self.nameEdit.setClearButtonEnabled(True)
        self.nameEdit.setFixedWidth(400)

        # set confirm and cancel button
        width = self.confirmBt.width() * 2
        self.confirmBt.setFixedWidth(width)
        self.cancelBt.setFixedWidth(width)
        font = self.confirmBt.font()
        font.setPixelSize(20)
        self.confirmBt.setFont(font)
        self.cancelBt.setFont(font)

        # add icon libraries to stack widget
        self.iconView.addWidget(self.fluentIL)
        self.iconView.addWidget(self.CustomIL)

        self.__initLayout()
        self.__connectSignalToSlot()
        self.__setQss()

    def __initLayout(self):
        titleAndEditLayout = QVBoxLayout()
        titleAndBtLayout = QHBoxLayout()
        layoutAndILLayout = QVBoxLayout()
        confirmAndCancelLayout = QHBoxLayout()

        # add title and edit to layout
        titleAndEditLayout.addWidget(self.nameEditLabel)
        titleAndEditLayout.addWidget(self.nameEdit)
        titleAndEditLayout.setContentsMargins(20, 0, 0, 0)

        # add icon label and switch button to layout
        titleAndBtLayout.addWidget(self.iconLabel)
        titleAndBtLayout.addItem(QSpacerItem(0, 0, hPolicy=QSizePolicy.Policy.Expanding))
        titleAndBtLayout.addWidget(self.switchBt)
        titleAndBtLayout.setContentsMargins(0, 0, 30, 0)

        # add titleAndBtLayout and iconView to layout
        layoutAndILLayout.addLayout(titleAndBtLayout)
        layoutAndILLayout.addWidget(self.iconView)
        layoutAndILLayout.setContentsMargins(20, 0, 0, 0)

        # add confirm and cancel button to layout
        confirmAndCancelLayout.addItem(QSpacerItem(0, 0, hPolicy=QSizePolicy.Policy.Expanding))
        confirmAndCancelLayout.addWidget(self.confirmBt)
        confirmAndCancelLayout.addItem(QSpacerItem(0, 0, hPolicy=QSizePolicy.Policy.Expanding))
        confirmAndCancelLayout.addWidget(self.cancelBt)
        confirmAndCancelLayout.addItem(QSpacerItem(0, 0, hPolicy=QSizePolicy.Policy.Expanding))
        confirmAndCancelLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # add all layout to main layout
        mainLayout = self.__mainLayout
        mainLayout.addWidget(self.titleLabel)
        mainLayout.addLayout(titleAndEditLayout)
        mainLayout.addLayout(titleAndBtLayout)
        mainLayout.addLayout(layoutAndILLayout)
        mainLayout.addLayout(confirmAndCancelLayout)
        mainLayout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        mainLayout.setContentsMargins(10, 10, 10, 10)

    def __setQss(self):
        self.iconView.setStyleSheet(
            """
            background-color: rgba(0, 0, 0, 0);
            border: none;
            """
        )


class DoThingInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__mainLayout = QVBoxLayout(self)
        self.pivot = SegmentedToggleToolWidget(self)
        self.stackWidget = StackedWidget(self)
        self.viewPage = ViewPage(self)
        self.addCardPage = AddCardPage(self)
        self.stackWidget.addWidget(self.viewPage)
        self.stackWidget.addWidget(self.addCardPage)

        self.__initWidget()

    def __initWidget(self):
        self.setObjectName("DoThingInterface")
        self.resize(800, 600)

        # init pivot items
        self.pivot.addItem("view", FluentIcon.VIEW,
                           onClick=lambda: self.stackWidget.setCurrentIndex(0))
        self.pivot.addItem("add", FluentIcon.ADD,
                           onClick=lambda: self.stackWidget.setCurrentIndex(1))
        self.pivot.setFixedSize(self.pivot.size())
        self.pivot.setCurrentItem("view")

        self.__initLayout()

    def __initLayout(self):
        # main layout
        self.__mainLayout.addWidget(self.pivot)
        self.__mainLayout.addWidget(self.stackWidget)
        self.__mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.__mainLayout.setSpacing(5)
        self.__mainLayout.setContentsMargins(10, 10, 0, 0)


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    w = DoThingInterface()
    w.show()
    sys.exit(app.exec())
