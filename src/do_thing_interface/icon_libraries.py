import sys
import threading
import time
from abc import abstractmethod
from typing import Union, Optional, Dict

from PyQt6.QtCore import QEasingCurve, Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QButtonGroup
from qfluentwidgets import (SmoothScrollArea, FlowLayout, FluentIcon,
                            ToggleToolButton)


class IconLibraryBase(SmoothScrollArea):
    addIconSignal = pyqtSignal(FluentIcon)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._view = QWidget(self)
        self._flowLayout = FlowLayout(self._view)
        self._iconSize = 64
        self._selected: Optional[ToggleToolButton] = None
        self.icons = []
        self.iconToWidget: Dict[Union[str, FluentIcon], ToggleToolButton] = {}
        self.widgetToIcon: Dict[ToggleToolButton, Union[str, FluentIcon]] = {}
        self.buttonGroup = QButtonGroup(self)

        # customize scroll animation
        self.setScrollAnimation(Qt.Orientation.Vertical, 400, QEasingCurve.Type.OutQuint)
        self.setScrollAnimation(Qt.Orientation.Horizontal, 400, QEasingCurve.Type.OutQuint)

        self.addIconSignal.connect(self.addIcon)

        self.horizontalScrollBar().setValue(1900)
        self.setWidget(self._view)
        self._setQss()

    def addIcon(self, icon: Union[str, FluentIcon]):
        if self.isExistent(icon):
            return

        # add to view
        iconWidget = ToggleToolButton(icon, self._view)
        iconWidget.setFixedSize(self._iconSize, self._iconSize)
        iconWidget.clicked.connect(lambda: self.setCurrentIcon(iconWidget))
        self._flowLayout.addWidget(iconWidget)

        # add to list and set and map
        self.icons.append(icon)
        self.iconToWidget[icon] = iconWidget
        self.widgetToIcon[iconWidget] = icon

        self.updateViewGeometry()

    def disSelect(self):
        if self._selected is not None:
            self._selected.setChecked(False)
            self._selected = None

    def isExistent(self, icon: Union[str, FluentIcon]) -> bool:
        return icon in self.iconToWidget

    def toIcon(self, widget: ToggleToolButton) -> Union[str, FluentIcon]:
        return self.widgetToIcon[widget]

    def removeIcon(self, icon: Union[str, FluentIcon]):
        if not self.isExistent(icon):
            return

        # remove from view
        iconWidget = self.iconToWidget[icon]
        self.icons.remove(icon)
        self.iconToWidget.pop(icon)
        self.widgetToIcon.pop(iconWidget)
        self._flowLayout.removeWidget(iconWidget)
        iconWidget.deleteLater()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.updateViewGeometry()

    @abstractmethod
    def reload(self):
        pass

    def getSelectedIcon(self) -> Union[str, FluentIcon]:
        return self.toIcon(self._selected)

    def setIconSize(self, size: int):
        self._iconSize = size
        for icon in self.icons:
            self.iconToWidget[icon].setFixedSize(size, size)
        self.updateViewGeometry()

    def setCurrentIcon(self, widget: ToggleToolButton):
        if self._selected is None:
            self._selected = widget
        else:
            if self._selected is widget:
                widget.setChecked(True)
            else:
                self._selected.setChecked(False)
                self._selected = widget

    def _setQss(self):
        self.setStyleSheet(
            """
            IconLibrariesBase {
                background-color: #fbfcfd;
                border-radius: 5px;
            };
            """
        )
        self._view.setStyleSheet(
            """
            QWidget {
                background-color: #f3f3f3;
                border-radius: 5px;
            }
            """
        )

    def updateViewGeometry(self):
        width, sliderWidth = self.width(), 20
        hSpacing, vSpacing = self._flowLayout.horizontalSpacing(), self._flowLayout.verticalSpacing()
        oneLine = (width - sliderWidth) // (self._iconSize + hSpacing)
        if oneLine == 0:
            return
        number = len(self.icons)
        row = number // oneLine + 1
        height = row * (self._iconSize + vSpacing)
        self._view.setGeometry(0, 0, width - sliderWidth, height + vSpacing)


class FluentIconLibrary(IconLibraryBase):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(800, 600)
        self.setIconSize(80)
        threading.Thread(target=self.initIcon).start()  # sub-thread loading UI

    def initIcon(self):
        for icon in FluentIcon:
            self.addIconSignal.emit(icon)

    def reload(self):
        pass


class CustomIconLibrary(IconLibraryBase):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(800, 600)
        self.setIconSize(80)
        threading.Thread(target=self.initIcon).start()  # sub-thread loading UI

    def initIcon(self):
        for icon in [FluentIcon.ADD, FluentIcon.CAR, FluentIcon.SAVE]:
            self.addIconSignal.emit(icon)

    def reload(self):
        pass


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    start = time.time()
    w = FluentIconLibrary()
    w.show()
    print(time.time() - start)
    sys.exit(app.exec())
