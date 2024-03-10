import time
import threading
import uuid
from copy import deepcopy
from typing import Union, Callable

from PyQt6.QtCore import pyqtSignal, QObject, Qt, QEasingCurve
from PyQt6.QtWidgets import (QStackedWidget, QWidget, QVBoxLayout, QHBoxLayout,
                             QSpacerItem, QSizePolicy)
from qfluentwidgets import (BreadcrumbBar, FlowLayout, IconWidget, SubtitleLabel,
                            TransparentPushButton, ToolButton, FluentIcon,
                            ElevatedCardWidget, SmoothScrollArea)

import config as cfg
from log import logger
from src.source_data import SourceData
from src.manager import SDManager
from src.utils import isFluentIconStr, strToFluentIcon
from src.widgets import CardLayout


class CardItemData(QObject):
    def __init__(self, d: dict, parent: Union[SourceData, "CardItemData"] = None):
        super().__init__(parent)
        self._parent = parent
        self.dict = d
        self.subItems = [CardItemData(d, self) for d in d["subItems"]]
        self.__connectSignalToSlot()

    def addSubItem(self, name: str, icon: str) -> None:
        defaultData = deepcopy(cfg.defaultData)
        defaultData["name"] = name
        defaultData["icon"] = icon
        defaultData["uid"] = uuid.uuid4().hex
        self.subItems.append(CardItemData(defaultData, self))
        self.updateData.emit()

    @property
    def uid(self) -> str:
        return self.dict["uid"]

    @property
    def name(self) -> str:
        return self.dict["name"]

    @property
    def icon(self) -> str:
        return self.dict["icon"]

    @property
    def hours(self) -> float:
        return self.dict["hours"]

    # 总时常
    @property
    def totalHours(self) -> float:
        return round(self.hours + sum([item.totalHours for item in self.subItems]), 1)

    def setUid(self, uid: str) -> None:
        self.dict["uid"] = uid
        self.updateData.emit()

    def setName(self, name: str) -> None:
        self.dict["name"] = name
        self.updateData.emit()

    def setIcon(self, icon: str) -> None:
        self.dict["icon"] = icon
        self.updateData.emit()

    def setHours(self, hours: float) -> None:
        self.dict["hours"] = hours
        self.updateData.emit()

    def sourceUpdatedSlot(self, obj: QObject) -> None:
        # 自己触发的信号不处理
        if obj is self:
            return
        self.dataUpdated.emit()

    def __connectSignalToSlot(self):
        parent = self._parent
        if isinstance(parent, SourceData):
            self.updateData.connect(parent.dataChanged)
            self.updateData.connect(lambda: parent.updateData.emit(self))
            parent.dataUpdated.connect(self.sourceUpdatedSlot)
        elif isinstance(parent, CardItemData):
            self.updateData.connect(parent.updateData)
            parent.dataUpdated.connect(self.dataUpdated)
        else:
            raise TypeError("Parent type error")

    dataUpdated = pyqtSignal()
    updateData = pyqtSignal()


# 页面内的元素
class PageCardItem(ElevatedCardWidget):
    def __init__(self, data: CardItemData, parent=None):
        super().__init__(parent)
        self.data = data
        self.hLayout = QHBoxLayout(self)
        self.iconWidget = IconWidget(self)
        self.nameLabel = SubtitleLabel(self)
        self.timeBt = TransparentPushButton(self)
        self.addBt = ToolButton(FluentIcon.ADD, self)
        self.deleteBt = ToolButton(FluentIcon.DELETE, self)
        self.splitBt = ToolButton(FluentIcon.ZOOM, self)
        self.doThingBt = ToolButton(FluentIcon.CALENDAR, self)
        self.__initWidget()

    def __initWidget(self):
        self.setBorderRadius(10)
        if isFluentIconStr(self.data.icon):
            self.iconWidget.setIcon(strToFluentIcon(self.data.icon))
        self.iconWidget.setFixedSize(64, 64)
        self.nameLabel.setText(self.data.name)
        self.nameLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timeBt.setText(f"{self.data.totalHours} H")
        self.setFixedSize(380, 170)

        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        leftMainLayout = CardLayout(True)
        leftMainLayout.addWidget(self.nameLabel)
        leftMainLayout.addWidget(self.timeBt)
        leftMainLayout.setBorderRadius(5)

        toolCardLayout = CardLayout(False)
        toolCardLayout.addWidget(self.doThingBt)
        toolCardLayout.addWidget(self.splitBt)
        toolCardLayout.addWidget(self.addBt)
        toolCardLayout.addWidget(self.deleteBt)
        toolCardLayout.setBorderRadius(5)

        iconCardLayout = CardLayout(False)
        iconCardLayout.addWidget(self.iconWidget)
        iconCardLayout.setBorderRadius(5)

        rightMainLayout = QVBoxLayout()
        rightMainLayout.addWidget(toolCardLayout)
        rightMainLayout.addWidget(iconCardLayout)

        self.hLayout.addWidget(leftMainLayout, 1)
        self.hLayout.addLayout(rightMainLayout, 0)
        self.hLayout.setContentsMargins(10, 10, 10, 10)
        self.hLayout.setSpacing(10)

    def __dataUpdatedSlot(self):
        self.nameLabel.setText(self.data.name)
        self.timeBt.setText(f"{self.data.totalHours} H")
        if isFluentIconStr(self.data.icon):
            self.iconWidget.setIcon(strToFluentIcon(self.data.icon))

    def __connectSignalToSlot(self):
        self.data.dataUpdated.connect(self.__dataUpdatedSlot)


# 页面
class ProjectEditPage(SmoothScrollArea):
    def __init__(self, datas: list[CardItemData], parent=None,
                 splitBtCallback: Callable[[str, str, list], None] = None,
                 doThingBtCallback: Callable[[CardItemData], None] = None):
        logger.debug("---ProjectEditPage initializing---")
        super().__init__(parent)
        self._view = QWidget(self)
        self._view.setObjectName("ScrollAreaWidget")
        self._flowLayout = FlowLayout(self._view)
        self._datas = datas
        self._map = {}  # type: dict[CardItemData, PageCardItem]
        self.splitBtCallback = splitBtCallback
        self.doThingBtCallback = doThingBtCallback
        self.addCardItem.connect(self.addItem)

        # init scroll area
        self.setScrollAnimation(Qt.Orientation.Vertical, 400, QEasingCurve.Type.OutQuint)
        self.setScrollAnimation(Qt.Orientation.Horizontal, 400, QEasingCurve.Type.OutQuint)
        self.horizontalScrollBar().setValue(1900)
        self.setWidget(self._view)
        self._setQss()

        self._subThreadLoad()
        logger.debug("---ProjectEditPage initialized---")

    def addItem(self, data: CardItemData):
        card = PageCardItem(data, self)
        card.splitBt.clicked.connect(lambda: self.splitBtCallback(card.data.uid, card.data.name, card.data.subItems))
        card.doThingBt.clicked.connect(lambda: self.doThingBtCallback(card.data))
        self._flowLayout.addWidget(card)
        self._map[data] = card
        self.updateViewGeometry()

    def removeItem(self, data: CardItemData):
        card = self._map.pop(data)
        self._flowLayout.removeWidget(card)
        card.deleteLater()
        self.updateViewGeometry()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.updateViewGeometry()

    def updateViewGeometry(self):
        # card width = 380, card height = 170
        width, sliderWidth = self.width(), 20
        hSpacing, vSpacing = self._flowLayout.horizontalSpacing(), self._flowLayout.verticalSpacing()
        oneLine = (width - sliderWidth) // (380 + hSpacing)
        if oneLine == 0:
            return
        number = len(self._datas)
        row = number // oneLine + 1
        height = row * (170 + vSpacing)
        self._view.setGeometry(0, 0, width - sliderWidth, height + vSpacing)

    def _subThreadLoad(self):
        def forLoop():
            logger.debug("ProjectEditPage sub thread loading...")
            for data in self._datas:
                self.addCardItem.emit(data)
            logger.debug("ProjectEditPage sub thread loaded")

        threading.Thread(target=forLoop).start()

    def _setQss(self):
        self.setStyleSheet(
            """
            ProjectEditPage{
                border: none;
                background-color: #f7f9fc;
            }
            """
        )
        self._view.setStyleSheet(
            """
            #ScrollAreaWidget {
                background-color: #f7f9fc;
            }
            """
        )

    addCardItem = pyqtSignal(CardItemData)


# 管理和显示页面
class ProjectEditPageView(QWidget):
    def __init__(self, parent=None, doThingBtCallback: Callable[[CardItemData], None] = None):
        logger.debug("---ProjectEditPageView initializing---")
        super().__init__(parent)
        self._sourceDatas = SDManager.datas
        self._cardRootDatas = [CardItemData(d.dict, d) for d in self._sourceDatas]
        self._map: dict[str, ProjectEditPage] = {}
        self.vLayout = QVBoxLayout(self)
        self.breadcrumb = BreadcrumbBar(self)
        self.view = QStackedWidget(self)
        self.doThingBtCallback = doThingBtCallback
        self.__initWidget()
        self.addPage("root", "Root", self._cardRootDatas)
        logger.debug("---ProjectEditPageView initialized---")

    def addPage(self, routeKey: str, breadcrumbText: str, datas: list[CardItemData]):
        logger.debug(f"Add page: {routeKey}")
        page = ProjectEditPage(datas, self,
                               splitBtCallback=self.addPage,
                               doThingBtCallback=self.doThingBtCallback)
        self._map[routeKey] = page
        self.view.addWidget(page)
        self.view.setCurrentWidget(page)
        self.breadcrumb.addItem(routeKey, breadcrumbText)

    def removePage(self, routeKey: str):
        logger.debug(f"Remove page: {routeKey}")
        page = self._map.pop(routeKey)
        self.view.removeWidget(page)

    def setCurrentPage(self, routeKey: str):
        routeKeys = list(self._map.keys())
        index = routeKeys.index(routeKey)
        self.view.setCurrentIndex(index)
        for i in range(index + 1, len(routeKeys)):
            self.removePage(routeKeys[i])
        self.currentIndexChanged.emit(index)
        self.currentPageChanged.emit(routeKey)

    def __connectSignalToSlot(self):
        self.breadcrumb.currentItemChanged.connect(self.setCurrentPage)

    def __initWidget(self):
        # set breadcrumb font pixel size
        font = self.breadcrumb.font()
        font.setPixelSize(20)
        self.breadcrumb.setFont(font)

        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.vLayout.addWidget(self.breadcrumb)
        self.vLayout.addWidget(self.view)
        self.vLayout.setSpacing(10)

    currentIndexChanged = pyqtSignal(int)  # index
    currentPageChanged = pyqtSignal(str)  # route key


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    app = QApplication([])
    # w = PageCardItem(CardItemData(SDManager.datas[0].dict, SDManager.datas[0]))
    w = ProjectEditPageView()
    w.resize(800, 600)
    w.show()
    app.exec()
