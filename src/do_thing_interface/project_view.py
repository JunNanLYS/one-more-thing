import threading
import time
from typing import Callable

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget
from qfluentwidgets.window.stacked_widget import StackedWidget
from qfluentwidgets import FlowLayout

from log import logger
from src.do_thing_interface.time_item_card import TimeItemCard, CardData
from src.source_data import SourceData
from src.manager import SDManager


class ProjectPage(QWidget):
    def __init__(self, cardDatas: list, viewSubProject: Callable, parent=None):
        super().__init__(parent)
        self.cardDatas = cardDatas
        self.dataToWidget = {}
        self.callback = viewSubProject
        self.pageCardSet = set()
        self.flowLayout = FlowLayout(self)

        self.updateCard.connect(self.addCard)
        self.subThreadLoadUi()

    def addCard(self, data: CardData):
        card = TimeItemCard(data, self)
        card.viewSubProject.connect(lambda: self.callback(data))
        self.flowLayout.addWidget(card)
        self.dataToWidget[data] = card
        self.pageCardSet.add(data)

    def removeCard(self, data: CardData):
        w: TimeItemCard = self.dataToWidget[data]
        self.flowLayout.removeWidget(w)
        self.dataToWidget.pop(data)
        self.pageCardSet.remove(data)
        w.deleteLater()

    def subThreadLoadUi(self):
        def forLoop():
            start = time.time()
            logger.debug("Sub thread load ui")
            for data in self.cardDatas:
                if data in self.pageCardSet:
                    continue
                self.updateCard.emit(data)
            logger.debug("Sub thread load ui finished")
            logger.info(f"Sub thread load ui time: {time.time() - start}")

        threading.Thread(target=forLoop).start()

    updateCard = pyqtSignal(CardData)


class ProjectView(StackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.routeKeys = []
        self.routeKeyMap = {}
        self.sourceDatas = SDManager.datas
        self.cardDatas = [CardData(data.dict, data) for data in self.sourceDatas]

        self.pushPage("Root", self.cardDatas)
        self.__setQss()
        SDManager.sourceDataCreated.connect(self.rootPageAddCard)
        SDManager.sourceDataDeleted.connect(self.rootPageDeleteCard)

    @property
    def rootPage(self) -> ProjectPage:
        return self.routeKeyMap["Root"]

    def rootPageAddCard(self, sData: SourceData) -> None:
        self.cardDatas.append(CardData(sData.dict, sData))
        self.rootPage.subThreadLoadUi()

    def rootPageDeleteCard(self, sData: SourceData) -> None:
        cardData = None
        for d in self.cardDatas:
            if d.parent() is sData:
                cardData = d

        self.rootPage.removeCard(cardData)
        self.cardDatas.remove(cardData)

    def pushPage(self, routeKey: str, cardDatas: list[CardData]) -> None:
        page = ProjectPage(cardDatas, self.__VSPCallback, self)
        self.routeKeys.append(routeKey)
        self.routeKeyMap[routeKey] = page
        self.addWidget(page)
        self.setCurrentIndex(len(self.routeKeys) - 1)

    # 在PyQt6-Fluent-Widgets更新到1.5.1之后版本需要删除，因为已经修复内存泄漏问题
    def removeWidget(self, w: QWidget):
        index = self.view.indexOf(w)
        if index == -1:
            return

        self.view.aniInfos.pop(index)
        self.view.removeWidget(w)

    def setCurrentPage(self, routeKey: str):
        logger.debug(f"Set current page: {routeKey}")
        page = self.routeKeyMap.get(routeKey)
        if page is None:
            logger.warning(f"Page not found: {routeKey}")
            return

        index = self.indexOf(page)
        deleteList = self.routeKeys[index + 1:]
        self.routeKeys = self.routeKeys[:index + 1]
        for key in deleteList:
            page = self.routeKeyMap[key]
            self.removeWidget(page)
            self.routeKeyMap.pop(key)

    def __setQss(self):
        self.setStyleSheet(
            """
            border: none;
            """
        )

    def __VSPCallback(self, data: CardData):
        logger.debug(f"View sub project: {data.name}")
        self.pushPage(data.uid, data.subItems)
        self.updateBreadcrumb.emit(data.uid, data.name)

    updateBreadcrumb = pyqtSignal(str, str)
