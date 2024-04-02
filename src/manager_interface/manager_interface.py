import time
from collections import deque
from typing import Optional, Union, Callable

from PySide6.QtCore import Qt, QThread, Signal, QPoint, QObject
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QWidget, QTreeWidgetItem, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (TreeWidget, TitleLabel, RoundMenu, Action, FluentIcon,
                            MessageBoxBase, SubtitleLabel, LineEdit,
                            MessageBox, StrongBodyLabel)

import config as cfg
from log import logger
from src.manager import SDManager
from src.py_qobject import PyQDict, PyQList
from src.source_data import SourceData
from src.utils import JsonDataStorage, getLabelBoundingRect, addSubItem, removeSubItem


class AddDataDialog(MessageBoxBase):
    def __init__(self, title: str, nameText: str, parent):
        super().__init__(parent)
        self.titleLb = SubtitleLabel(title, self)
        self.nameEdit = LineEdit(self)
        self.nameEdit.setPlaceholderText(nameText)
        self.nameEdit.setClearButtonEnabled(True)

        self.viewLayout.addWidget(self.titleLb)
        self.viewLayout.addWidget(self.nameEdit)

        self.yesButton.setText("Confirm")
        self.cancelButton.setText("Cancel")

        self.widget.setMinimumWidth(350)
        self.yesButton.setDisabled(True)

        self.nameEdit.textChanged.connect(self.onTextChanged)

    def onTextChanged(self, text: str):
        self.yesButton.setDisabled(text == "")


class EditDataDialog(MessageBoxBase):
    def __init__(self, _dict: PyQDict, parent):
        super().__init__(parent)
        self.titleLb = SubtitleLabel("Edit", self)
        self.nameLb = StrongBodyLabel("Project name", self)
        self.nameEdit = LineEdit(self)
        self.nameEdit.setClearButtonEnabled(True)
        self.nameEdit.setText(_dict["name"])

        self.nameLayout = QHBoxLayout(self)
        self.nameLayout.addWidget(self.nameLb)
        self.nameLayout.addWidget(self.nameEdit)

        self.viewLayout.addWidget(self.titleLb)
        self.viewLayout.addLayout(self.nameLayout)

        self.nameEdit.textChanged.connect(self.onTextChanged)

    def onTextChanged(self, text: str):
        self.yesButton.setDisabled(text == "")


class TreeWidgetItem(QTreeWidgetItem):
    def __init__(self, _dict: PyQDict, parent: Union[None, "TreeWidgetItem"]):
        super().__init__()
        self.__parent = parent
        self.dict = _dict
        self.map: dict[PyQDict, "TreeWidgetItem"] = {}
        self.setText(0, self.dict["name"])

        # set font pixel size
        font = self.font(0)
        font.setPixelSize(20)
        self.setFont(0, font)

        # connect signal to slot
        try:
            _list: PyQList = self.dict["subItems"]
        except KeyError:
            _list = PyQList()
            _list.valueChanged.connect(self.dict.valueChanged, Qt.ConnectionType.UniqueConnection)
            self.dict["subItems"] = _list
        _list.elementAppended.connect(self.addChild)
        _list.elementRemoved.connect(self.removeChild)
        self.dict.valueChanged.connect(self.updateUI)

    def addChild(self, _dict: PyQDict) -> "TreeWidgetItem":
        child = TreeWidgetItem(_dict, self)
        self.map[_dict] = child
        super().addChild(child)
        return child

    def removeChild(self, _dict: PyQDict):
        child = self.map.pop(_dict)
        super().removeChild(child)
        del child

    def updateUI(self):
        self.setText(0, self.dict["name"])

    def parent(self) -> Union["TreeWidgetItem", None]:
        return self.__parent


def createTreeWidgetItem(_dict: PyQDict, parent: Union[None, TreeWidgetItem] = None) -> TreeWidgetItem:
    root = TreeWidgetItem(_dict, parent)
    q = deque([root])
    while q:
        parent = q.popleft()
        for child in parent.dict["subItems"]:
            _next = parent.addChild(child)
            q.append(_next)
    return root


class LazyTreeWidget(TreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.currentItem: Optional[TreeWidgetItem] = None
        self.menu = RoundMenu(parent=self)
        self.map: dict[PyQDict, TreeWidgetItem] = {}
        self.sourceDatas = SDManager.datas
        self.setBorderVisible(True)
        self.setBorderRadius(5)
        self.setIndentation(40)

        SDManager.dataAdded.connect(self.__onSourceDataAppended)
        SDManager.dataRemoved.connect(self.__onSourceDataRemoved)
        self.__initMenu()
        self.addItemSignal.connect(self.__onAddTreeItem)
        self.updateUI()

    def addTopLevelItem(self, item: TreeWidgetItem) -> None:
        self.map[item.dict] = item
        super().addTopLevelItem(item)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.MouseButton.RightButton:
            self.currentItem = self.itemAt(e.pos())
            self.showMenu(self.mapToGlobal(e.pos()))
            return
        super().mousePressEvent(e)

    def updateUI(self):
        if len(self.sourceDatas) <= 100:
            for data in self.sourceDatas:
                item = createTreeWidgetItem(data.storage.dict)
                self.addTopLevelItem(item)
        else:
            class Worker(QThread):
                def __init__(self, datas, signal):
                    super().__init__(None)
                    self.datas = datas
                    self.signal = signal

                def run(self) -> None:
                    for _data in self.datas:
                        self.signal.emit(_data.storage)
                        time.sleep(0.05)
                    self.finished.emit()

            self.worker = Worker(self.sourceDatas, self.addItemSignal)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker.start()

    def showMenu(self, pos: QPoint):
        self.menu.move(pos)
        if self.currentItem is None:
            for action in self.menu.actions():
                action.setEnabled(action.text() not in ("Add", "Delete", "Edit"))
        else:
            for action in self.menu.actions():
                action.setEnabled(True)
        self.menu.show()

    def __onAddTreeItem(self, storage: JsonDataStorage):
        item = createTreeWidgetItem(storage.dict)
        self.addTopLevelItem(item)

    def __onAddSubItem(self):
        dialog = AddDataDialog(
            title="Add sub item",
            nameText="Input sub item name",
            parent=self.window()
        )
        default = cfg.getDefaultData()

        def onConfirm():
            default["name"] = dialog.nameEdit.text()
            addSubItem(self.currentItem.dict, default)

        dialog.yesButton.clicked.connect(onConfirm)
        dialog.exec()

    def __onEdit(self):
        _dict = self.currentItem.dict
        dialog = EditDataDialog(_dict, self.window())

        def onConfirm():
            _dict["name"] = dialog.nameEdit.text()

        dialog.yesButton.clicked.connect(onConfirm)
        dialog.exec()

    def __onRemoveSubItem(self):
        dialog = MessageBox(
            title="Waring",
            content="Are you sure to delete this item?",
            parent=self.window()
        )

        def onConfirm():
            parent = self.currentItem.parent()
            removeSubItem(parent.dict, self.currentItem.dict)

        dialog.yesSignal.connect(onConfirm)
        dialog.exec()

    def __onAddSourceData(self):
        dialog = AddDataDialog(
            title="Add Source Data",
            nameText="Input project name",
            parent=self.window()
        )

        def onConfirm():
            SDManager.addData(dialog.nameEdit.text(), "icon")

        dialog.yesButton.clicked.connect(onConfirm)
        dialog.yesButton.setText("Confirm")
        dialog.cancelButton.setText("Cancel")
        dialog.exec()

    def __onDeleteSourceData(self):
        dialog = MessageBox(
            title="Warning",
            content=
            "Are you sure you want to delete the source project, "
            "which will cause all sub-projects to disappear including itself.",
            parent=self.window()
        )

        def onConfirm():
            SDManager.removeData(self.currentItem.dict)

        dialog.yesSignal.connect(onConfirm)
        dialog.yesButton.setText("Confirm")
        dialog.cancelButton.setText("Cancel")
        dialog.exec()

    def __onDeleteItem(self):
        isRoot = self.currentItem.parent() is None
        if isRoot:
            self.__onDeleteSourceData()
        else:
            self.__onRemoveSubItem()

    def __onSourceDataAppended(self, data: SourceData):
        self.__onAddTreeItem(data.storage)

    def __onSourceDataRemoved(self, data: SourceData):
        _dict = data.storage.dict
        item = self.map.pop(_dict)
        self.takeTopLevelItem(self.indexOfTopLevelItem(item))
        del item

    def __initMenu(self):
        add = Action(FluentIcon.ADD, "Add")
        add.triggered.connect(self.__onAddSubItem)
        edit = Action(FluentIcon.EDIT, "Edit")
        edit.triggered.connect(self.__onEdit)
        delete = Action(FluentIcon.DELETE, "Delete")
        delete.triggered.connect(self.__onDeleteItem)
        addRoot = Action(FluentIcon.FOLDER_ADD, "Add root")
        addRoot.triggered.connect(self.__onAddSourceData)
        self.menu.addActions([
            add,
            edit,
            delete,
            addRoot,
        ])

    addItemSignal = Signal(JsonDataStorage)


class ManagerInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        start = time.time()
        logger.debug("---ManagerInterface initializing---")
        self.label = TitleLabel("Manage", self)
        self.treeWidget = LazyTreeWidget(self)
        self.vLayout = QVBoxLayout(self)
        self.__initWidget()
        logger.info(f"ManagerInterface Initialization time: {time.time() - start}")
        logger.debug("---ManagerInterface initialized---")

    def __initWidget(self):
        self.treeWidget.setHeaderHidden(True)
        rect = getLabelBoundingRect(self.label)
        self.label.setFixedSize(rect.width() + 5, rect.height())
        self.setObjectName("ManagerInterface")
        self.__initLayout()

    def __initLayout(self):
        self.label.move(36, 30)
        self.vLayout.addWidget(self.treeWidget)
        self.vLayout.setContentsMargins(36, 90, 36, 10)
        self.vLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
