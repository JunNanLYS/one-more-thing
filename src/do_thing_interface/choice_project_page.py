import time
from threading import Thread

from PyQt6.QtCore import Qt, QEasingCurve, pyqtSignal, QThread
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from qfluentwidgets import (ElevatedCardWidget, SubtitleLabel, SmoothScrollArea,
                            IconWidget, TransparentPushButton, FlowLayout,
                            BreadcrumbBar, PopUpAniStackedWidget)

from log import logger
from src.manager import SDManager
from src.py_qobject import PyQDict, PyQList

CARD_WIDTH = 240
CARD_HEIGHT = 100


class ProjectCard(ElevatedCardWidget):
    def __init__(self, _dict: PyQDict, parent=None):
        super().__init__(parent)
        self._dict = _dict
        self.iconWidget = IconWidget(self)
        self.name = SubtitleLabel(self)
        self.timeBt = TransparentPushButton(self)
        self.vLayout = QVBoxLayout(self)

        self.__initWidget()

    def resetText(self):
        def getTotalTime(_dict: PyQDict):
            return _dict["hours"] + sum([getTotalTime(d) for d in _dict.get("subItems", PyQList())])

        self.iconWidget.setIcon(self._dict["icon"])
        self.name.setText(self._dict["name"])
        self.timeBt.setText(f"{getTotalTime(self._dict)} H")

    def __connectSignalToSlot(self):
        self._dict.valueChanged.connect(self.onValueChanged)
        self.onValueChanged.connect(self.resetText)

    def __initWidget(self):
        self.resetText()
        self.iconWidget.setFixedSize(32, 32)
        self.timeBt.setFixedWidth(CARD_WIDTH // 2)
        self.setFixedSize(CARD_WIDTH, CARD_HEIGHT)
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        topLayout = QHBoxLayout()
        topLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        topLayout.setSpacing(10)
        topLayout.setContentsMargins(0, 0, 0, 0)
        topLayout.addWidget(self.iconWidget)
        topLayout.addWidget(self.name)

        bottomLayout = QHBoxLayout()
        bottomLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bottomLayout.setSpacing(10)
        bottomLayout.setContentsMargins(0, 0, 0, 0)
        bottomLayout.addWidget(self.timeBt)

        self.vLayout.addLayout(topLayout)
        self.vLayout.addLayout(bottomLayout)
        self.vLayout.setSpacing(10)
        self.vLayout.setContentsMargins(10, 10, 10, 10)
        self.vLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    onValueChanged = pyqtSignal()


class ProjectPage(SmoothScrollArea):
    def __init__(self, _list: PyQList, parent=None):
        super().__init__(parent)
        self.view = QWidget(self)
        self.view.setObjectName("ScrollAreaWidget")
        self.flowLayout = FlowLayout(self.view)
        self._list = _list
        self._map: dict[PyQDict, ProjectCard] = {}

        # customize scroll animation
        self.setScrollAnimation(Qt.Orientation.Vertical, 400, QEasingCurve.Type.OutQuint)
        self.setScrollAnimation(Qt.Orientation.Horizontal, 400, QEasingCurve.Type.OutQuint)

        self._setQss()
        self.__initWidget()

    def addWidget(self, obj: PyQDict):
        if not isinstance(obj, PyQDict):
            logger.error(f"Type of accident: {type(obj)}")
            return
        w = ProjectCard(obj, self)
        self.flowLayout.addWidget(w)
        self._map[obj] = w
        w.clicked.connect(lambda: self.cardClicked.emit(obj["uid"], obj["name"], obj["subItems"]))
        w.timeBt.clicked.connect(lambda: self.timeBtClicked.emit(obj))

    def removeWidget(self, obj: PyQDict):
        if not isinstance(obj, PyQDict):
            logger.error(f"Type of accident: {type(obj)}")
            return
        w = self._map[obj]
        self.flowLayout.removeWidget(w)
        self._map.pop(obj)
        w.deleteLater()

    def _setQss(self):
        self.setStyleSheet("""QScrollArea{background: transparent; border: none}""")
        self.view.setStyleSheet("""QWidget {background: transparent;}""")

    def __connectSignalToSlot(self):
        self._list.elementRemoved.connect(self.onRemoveWidget)
        self._list.elementAppended.connect(self.onAddWidget)
        self.onAddWidget.connect(self.addWidget)
        self.onRemoveWidget.connect(self.removeWidget)

    def __initWidget(self):
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.__initLayout()
        self.__connectSignalToSlot()
        self.__updateUI()

    def __initLayout(self):
        self.flowLayout.setHorizontalSpacing(10)
        self.flowLayout.setVerticalSpacing(10)

    def __updateUI(self):
        if len(self._list) <= 100:
            for d in self._list:
                self.addWidget(d)
        else:
            class Worker(QThread):
                def __init__(self, _list, signal):
                    super().__init__(None)
                    self.list = _list
                    self.signal = signal

                def run(self) -> None:
                    for _dict in self.list:
                        self.signal.emit(_dict)
                        time.sleep(0.05)
                    self.finished.emit()

            self.worker = Worker(self._list, self.onAddWidget)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker.start()

    onAddWidget = pyqtSignal(object)
    onRemoveWidget = pyqtSignal(object)
    cardClicked = pyqtSignal(str, str, PyQList)
    timeBtClicked = pyqtSignal(PyQDict)


class ChoiceProjectPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        logger.debug("---ChoiceProjectPage initializing---")
        start = time.time()
        self.breadcrumb = BreadcrumbBar(self)
        self.view = PopUpAniStackedWidget(self)
        self.vLayout = QVBoxLayout(self)
        self._dict: dict[str, ProjectPage] = {}
        self._rootPyQList = PyQList()
        self._rootPyQList.replaceList([d.storage.dict for d in SDManager.datas])

        self.__initWidget()
        self.addPage("root", "Main", self._rootPyQList)
        logger.info(f"ChoiceProjectPage Initialization time: {time.time() - start}")
        logger.debug("---ChoiceProjectPage initialized---")

    def addPage(self, routeKey: str, name: str, datas: PyQList):
        if routeKey in self._dict:
            logger.error(f"Page {routeKey} already exists")
            return
        page = ProjectPage(datas, self)
        self.view.addWidget(page)
        self._dict[routeKey] = page
        self.breadcrumb.addItem(routeKey, name)
        page.cardClicked.connect(self.addPage)
        page.timeBtClicked.connect(self.timeBtClicked)
        logger.debug(f"Page {routeKey} added")

    def removePage(self, routeKey: str):
        if routeKey not in self._dict:
            logger.error(f"Page {routeKey} not exists")
            return
        page = self._dict.pop(routeKey)
        self.view.removeWidget(page)
        page.deleteLater()
        del page
        logger.debug(f"Page {routeKey} removed")

    def setCurrentPage(self, index: int):
        logger.debug(f"Set current index to {index}")
        self.view.setCurrentIndex(index)
        routeKeys = list(self._dict.keys())
        deleteKeys = routeKeys[index + 1:]
        for key in deleteKeys:
            self.removePage(key)
        del deleteKeys

    def __connectSignalToSlot(self):
        self.breadcrumb.currentIndexChanged.connect(self.setCurrentPage)
        SDManager.dataRemoved.connect(lambda data: self._rootPyQList.remove(data.storage.dict))
        SDManager.dataAdded.connect(lambda data: self._rootPyQList.append(data.storage.dict))

    def __initWidget(self):
        font = self.breadcrumb.font()
        font.setPixelSize(20)
        self.breadcrumb.setFont(font)

        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.vLayout.addWidget(self.breadcrumb)
        self.vLayout.addWidget(self.view)
        self.vLayout.setContentsMargins(0, 0, 0, 0)
        self.vLayout.setSpacing(0)
        self.vLayout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

    timeBtClicked = pyqtSignal(PyQDict)


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    app = QApplication([])
    _w = ChoiceProjectPage()
    _w.resize(800, 600)
    _w.show()
    app.exec()
