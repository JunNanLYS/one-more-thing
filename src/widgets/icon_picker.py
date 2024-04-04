from typing import Callable

from PySide6.QtCore import Qt, QEasingCurve, Signal, QPoint
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from qfluentwidgets import (FlowLayout, setFont, SmoothScrollArea, SimpleCardWidget,
                            ToggleToolButton)

from .icon import OMThingIcon


class IconWidget(ToggleToolButton):
    def __init__(self, icon: OMThingIcon, parent: QWidget):
        super().__init__(parent)
        self.setIcon(icon)
        self.icon = icon
        self.setFixedSize(32, 32)


class IconGroup(QWidget):
    def __init__(self, title: str, onClicked: Callable[[IconWidget], None], parent: QWidget):
        super().__init__(parent)
        self._titleLb = QLabel(title, self)
        self._vLayout = QVBoxLayout(self)
        self._iconLayout = FlowLayout()

        self._vLayout.addWidget(self._titleLb)
        self._vLayout.addLayout(self._iconLayout, 1)
        self._vLayout.setContentsMargins(0, 0, 0, 0)
        self._vLayout.setSpacing(12)
        self._vLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._iconLayout.setVerticalSpacing(5)
        self._iconLayout.setHorizontalSpacing(5)

        setFont(self._titleLb, 20)
        self._titleLb.adjustSize()

        self.onClicked = onClicked

    def addIcon(self, icon: OMThingIcon) -> None:
        iconBt = IconWidget(icon, self)
        iconBt.clicked.connect(lambda: self.onClicked(iconBt))
        self._iconLayout.addWidget(iconBt)

    def addIcons(self, icons: list[OMThingIcon]) -> None:
        for icon in icons:
            self.addIcon(icon)


class IconPicker(SimpleCardWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._scrollArea = SmoothScrollArea(self)
        self._scrollWidget = QWidget(self._scrollArea)
        self._expandLayout = QVBoxLayout(self._scrollWidget)
        self._vLayout = QVBoxLayout(self)

        self.currentWidget = None

        self.Microsoft365Group = IconGroup(
            title="Microsoft 365",
            onClicked=self.onClicked,
            parent=self._scrollWidget
        )
        self.defaultGroup = IconGroup(
            title="Default",
            onClicked=self.onClicked,
            parent=self._scrollWidget
        )

        self._setQss()
        self.__initWidget()

    def flyout(self, target: QWidget, parent: QWidget) -> None:
        pos = target.pos() + QPoint(target.width() + 10, 0)
        self.setParent(parent)
        self.move(pos)
        self.show()

    def onClicked(self, widget: IconWidget) -> None:
        if self.currentWidget is widget:
            return
        if self.currentWidget:
            self.currentWidget.setChecked(False)
        widget.setChecked(True)
        self.currentWidget = widget
        self.currentChanged.emit(widget.icon)

    def _setQss(self):
        self._scrollArea.setStyleSheet("QScrollArea{background: transparent; border: none;}")
        self._scrollWidget.setStyleSheet("QWidget{background: transparent;}")

    def __initWidget(self) -> None:
        self._scrollArea.setWidget(self._scrollWidget)
        self._scrollArea.setWidgetResizable(True)
        self._scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scrollArea.setScrollAnimation(Qt.Orientation.Vertical, 400, QEasingCurve.OutQuint)
        self._scrollArea.setScrollAnimation(Qt.Orientation.Horizontal, 400, QEasingCurve.OutQuint)

        self.setFixedSize(210, 200)

        self.__initGroup()
        self.__initLayout()

    def __initGroup(self) -> None:
        microsoft = [
            OMThingIcon.AI,
            OMThingIcon.DOCX,
            OMThingIcon.PPT,
            OMThingIcon.PS,
            OMThingIcon.XLSX,
        ]
        default = [
            OMThingIcon.BASKETBALL,
            OMThingIcon.BOOK,
            OMThingIcon.CAT,
            OMThingIcon.COFFEE,
            OMThingIcon.CHINESE,
            OMThingIcon.DOG,
            OMThingIcon.FISH,
            OMThingIcon.ENGLISH,
            OMThingIcon.EXERCISE,
            OMThingIcon.FISHING,
            OMThingIcon.GO_TO_WORK,
            OMThingIcon.MATH,
            OMThingIcon.RUNNING,
            OMThingIcon.WPS,
            OMThingIcon.WECHAT
        ]

        self.Microsoft365Group.addIcons(microsoft)
        self.defaultGroup.addIcons(default)

    def __initLayout(self) -> None:
        self._vLayout.addWidget(self._scrollArea)
        self._vLayout.setContentsMargins(0, 0, 0, 0)
        self._vLayout.setSpacing(0)

        self._expandLayout.addWidget(self.Microsoft365Group)
        self._expandLayout.addWidget(self.defaultGroup)

    currentChanged = Signal(OMThingIcon)
