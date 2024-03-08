import uuid
from typing import Optional, Union

from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout
from qfluentwidgets import (IconWidget, TitleLabel, PushButton,
                            TransparentPushButton, FluentIcon, ElevatedCardWidget,
                            CardWidget)

from log import logger
import config as cfg
from src.utils import isFluentIconStr, fluentIconToStr, strToFluentIcon
from src.source_data import SourceData


class CardData(QObject):
    def __init__(self, d: dict, parent: Union[SourceData, "CardData"]):
        super().__init__(parent)
        self.__parent = parent
        self.__dict: dict = d
        self.__name: Optional[str] = None
        self.__icon: Optional[str, FluentIcon] = None
        self.__hours: Optional[float] = None
        self.__subItems: Optional[list["CardData"]] = None
        self.__uid: Optional[str] = None

        self.fromDict()
        self.__connectSignalToSlot()

    def addSubItem(self, name: str, icon: Union[str, FluentIcon]):
        logger.debug("Add child item")
        defaultDict = cfg.defaultFormat.copy()
        defaultDict["name"] = name
        defaultDict["icon"] = fluentIconToStr(icon)
        defaultDict["uid"] = uuid.uuid4().hex
        self.__dict["subItems"].append(defaultDict)
        self.__subItems.append(CardData(defaultDict, self))
        self.dataUpdated.emit()
        self.subItemCreated.emit()
        logger.debug("Child item added")

    def addTime(self, hours: int, minute: int):
        self.__hours += hours
        res = minute / 60
        self.__hours += res
        self.__hours = round(self.__hours, 1)
        self.dataUpdated.emit()

    @property
    def cumulativeTime(self) -> float:
        res = self.__hours + sum([item.cumulativeTime for item in self.subItems])
        return round(res, 1)

    def fromDict(self):
        m = self.__dict
        self.__name = m.get("name", "No name")
        self.__icon = m.get("icon", FluentIcon.ADD)
        self.__hours = m.get("hours", 0.0)
        self.__uid = m.get("uid", uuid.uuid4().hex)
        self.__subItems = [CardData(child, self) for child in m.get('subItems', [])]

        if isinstance(self.__icon, str) and isFluentIconStr(self.__icon):
            self.__icon = strToFluentIcon(self.__icon)

    @property
    def hours(self) -> float:
        return self.__hours

    @property
    def icon(self):
        return self.__icon

    @property
    def subItems(self) -> list["CardData"]:
        return self.__subItems

    def setName(self, name: str):
        self.__name = name
        self.dataUpdated.emit()

    @property
    def uid(self):
        return self.__uid

    @property
    def name(self):
        return self.__name

    def __connectSignalToSlot(self):
        parent = self.__parent
        if isinstance(parent, SourceData):
            self.dataUpdated.connect(parent.dataChanged)
            self.dataUpdated.connect(parent.updateData)
        else:
            self.dataUpdated.connect(parent.dataUpdated)

    dataUpdated = pyqtSignal()
    subItemCreated = pyqtSignal()
    subItemDeleted = pyqtSignal()


class TimeItemCard(ElevatedCardWidget):
    def __init__(self, data: CardData, parent):
        super().__init__(parent)
        self.__mainLayout = QHBoxLayout(self)
        self.__hBoxLayout = QHBoxLayout(self)
        self.__vBoxLayout = QVBoxLayout(self)
        self._data = data
        self.iconWidget = None
        self.titleLabel = None
        self.timeButton = None
        self.viewSProjectBt = None

        self.__initWidget()

    @property
    def icon(self) -> str:
        return self._data.icon

    @property
    def name(self) -> str:
        return self._data.name

    @property
    def subItems(self) -> list[CardData]:
        return self._data.subItems

    @property
    def uid(self):
        return self._data.uid

    def __connectSignalToSlot(self):
        self.viewSProjectBt.clicked.connect(self.__viewSubProjectSlot)
        self._data.dataUpdated.connect(self.__dataUpdatedSlot)

    def __dataUpdatedSlot(self):
        self.iconWidget.setIcon(self._data.icon)
        self.titleLabel.setText(self._data.name)
        self.timeButton.setText(f"{self._data.cumulativeTime} Hours")

    def __viewSubProjectSlot(self):
        self.viewSubProject.emit()

    def __initWidget(self):
        """ init widget
        :return: None
        """
        self.iconWidget = IconWidget(self.icon, self)
        self.titleLabel = TitleLabel(self.name, self)
        self.timeButton = TransparentPushButton(f"{self._data.cumulativeTime} Hours", self)
        self.viewSProjectBt = PushButton("View Subproject", self)

        # set iconWidget fixed size
        self.iconWidget.setFixedSize(64, 64)

        # set timeButton font
        font = QFont(self.timeButton.font())
        font.setPointSize(15)
        font.setBold(True)
        self.timeButton.setFont(font)

        # set titleLabel alignment
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # set TimeItemCard fixed size
        self.setFixedSize(270, 140)

        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        """ init layout
        :return: None
        """
        # h layout
        self.__hBoxLayout.addWidget(self.iconWidget)

        # v layout
        self.__vBoxLayout.addWidget(self.titleLabel)
        self.__vBoxLayout.addWidget(self.timeButton)
        self.__vBoxLayout.addWidget(self.viewSProjectBt)
        self.__vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignRight)

        # main layout
        self.__mainLayout.addLayout(self.__hBoxLayout)
        self.__mainLayout.addLayout(self.__vBoxLayout)
        self.__mainLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    viewSubProject = pyqtSignal()


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication
    from src.manager import SDManager

    app = QApplication(sys.argv)
    cardData = CardData(SDManager.datas[1].dict, SDManager.datas[1])
    card = TimeItemCard(cardData, None)
    card.show()
    app.exec()
