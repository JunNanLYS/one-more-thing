from collections import deque
from typing import Callable, Deque

from PySide6.QtCore import (Property, Signal, QPropertyAnimation,
                            QPoint, QEasingCurve, Qt, QSize)
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QLabel, QWidget, QHBoxLayout
from qfluentwidgets import TitleLabel, qconfig, isDarkTheme


class PickerItem(QLabel):
    def __init__(self, time: str, parent=None, opacity=1.0, fontSize=50):
        super().__init__(parent)
        self.setText(time)
        self._textOpacity = opacity
        self.opacityAnimation = QPropertyAnimation(self, b"textOpacity")
        self.moveAnimation = QPropertyAnimation(self, b"pos")
        self.fontAnimation = QPropertyAnimation(self, b"fontSize")

        font = self.font()
        font.setPointSize(fontSize)
        font.setFamily("Segoe UI")
        self.setFont(font)
        self.setFixedSize(100, 100)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.updateUI()
        qconfig.themeChangedFinished.connect(self.updateUI)

    def getMetricsHeight(self):
        return self.fontMetrics().boundingRect(self.text()).height()

    def getMetricsWidth(self):
        return self.fontMetrics().boundingRect(self.text()).width()

    @Property(float)
    def textOpacity(self) -> float:
        return self._textOpacity

    @textOpacity.setter
    def textOpacity(self, value: float):
        self._textOpacity = value
        self.updateUI()

    def updateUI(self):
        if isDarkTheme():
            self.setStyleSheet(f"color: rgba(255, 255, 255, {self._textOpacity});")
        else:
            self.setStyleSheet(f"color: rgba(0, 0, 0, {self._textOpacity});")

    @Property(int)
    def fontSize(self) -> int:
        return self.font().pointSize()

    @fontSize.setter
    def fontSize(self, value: int):
        font = self.font()
        font.setPointSize(value)
        self.setFont(font)

    def startAnimation(self, pos: QPoint, opacity: float, duration: int, easingCurve: QEasingCurve.Type,
                       useOpacity=False, fontSize: int = None, onFinished: Callable = None):
        self.moveAnimation.setStartValue(self.pos())
        self.moveAnimation.setEndValue(pos)
        self.moveAnimation.setDuration(duration)
        self.moveAnimation.setEasingCurve(easingCurve)

        self.opacityAnimation.setStartValue(self._textOpacity)
        self.opacityAnimation.setEndValue(opacity)
        self.opacityAnimation.setDuration(duration)
        self.opacityAnimation.setEasingCurve(easingCurve)

        self.fontAnimation.setStartValue(self.font().pointSize())
        self.fontAnimation.setEndValue(fontSize)
        self.fontAnimation.setDuration(duration)
        self.fontAnimation.setEasingCurve(easingCurve)

        if onFinished:
            self.moveAnimation.finished.connect(onFinished)

        if useOpacity and fontSize:
            self.moveAnimation.start()
            self.opacityAnimation.start()
            self.fontAnimation.start()
        elif useOpacity:
            self.moveAnimation.start()
            self.opacityAnimation.start()
        else:
            self.moveAnimation.start()


class Picker(QWidget):
    def __init__(self, defaultTexts: list[str], parent=None):
        super().__init__(parent)
        self._acceptWheelEvent = True
        self._defaultTexts = defaultTexts
        self._duration = 80
        self._itemSize = QSize(100, 100)
        self._margin = (10, 10, 10, 10)  # left, top, right, bottom
        self._spacing = 10
        self.deque: Deque[PickerItem] = deque(maxlen=3)
        self.itemPosMap = {
            "top": QPoint(self._margin[0], self._margin[1]),
            "center": QPoint(self._margin[0], self._margin[1] + self._itemSize.height() + self._spacing),
            "bottom": QPoint(self._margin[0], self._margin[1] + 2 * (self._itemSize.height() + self._spacing))
        }
        self.__initWidget()

    def setAcceptWheelEvent(self, accept: bool) -> None:
        self._acceptWheelEvent = accept

    def default(self) -> None:
        if len(self.deque):
            for item in self.deque:
                item.deleteLater()
            self.deque.clear()
        for i, text in enumerate(self._defaultTexts):
            if i == 1:
                item = PickerItem(text, self, 1.0, 50)
            else:
                item = PickerItem(text, self, 0.6, 40)
            item.show()
            self.deque.append(item)
        self.deque[0].move(self.itemPosMap["top"])
        self.deque[1].move(self.itemPosMap["center"])
        self.deque[2].move(self.itemPosMap["bottom"])

    def floatUp(self, text: str) -> None:
        self._popLeftItem()
        floatUpItem = PickerItem(text, self, 0.6, 40)
        floatUpItem.move(self.itemPosMap["bottom"] + QPoint(0, self._itemSize.height()))
        floatUpItem.show()
        self.deque.append(floatUpItem)
        self.resetPosAnimation()

    def floatDown(self, text: str) -> None:
        self._popRightItem()
        floatUpItem = PickerItem(text, self, 0.6, 40)
        floatUpItem.move(self.itemPosMap["top"] - QPoint(0, self._itemSize.height()))
        floatUpItem.show()
        self.deque.appendleft(floatUpItem)
        self.resetPosAnimation()

    def getTopItemText(self) -> str:
        return self.deque[0].text()

    def getCenterItemText(self) -> str:
        return self.deque[1].text()

    def getBottomItemText(self) -> str:
        return self.deque[2].text()

    def getCurrentSelected(self) -> str:
        return self.getCenterItemText()

    def resetPosAnimation(self) -> None:
        idxToStr = ["top", "center", "bottom"]
        for i, item in enumerate(self.deque):
            pos = self.itemPosMap[idxToStr[i]]
            item.startAnimation(pos, 1.0 if i == 1 else 0.6, self._duration,
                                QEasingCurve.Type.InOutQuad, True,
                                fontSize=50 if i == 1 else 40)

    def wheelEvent(self, e: QWheelEvent) -> None:
        if not self._acceptWheelEvent:
            return
        elif any(item.moveAnimation.state() == QPropertyAnimation.State.Running for item in self.deque):
            return

        # 获取滚轮滚动的距离
        degrees = e.angleDelta().y() / 8
        steps = degrees / 15
        if steps > 0:
            self.wheelScrolled.emit("up")
        else:
            self.wheelScrolled.emit("down")
        e.accept()
        super().wheelEvent(e)

    def _popLeftItem(self) -> None:
        item = self.deque.popleft()
        pos = QPoint(item.x(), 0 - item.height())
        item.startAnimation(pos, 0.0, self._duration, QEasingCurve.Type.InOutQuad,
                            True, onFinished=item.deleteLater)

    def _popRightItem(self) -> None:
        item = self.deque.pop()
        pos = QPoint(item.x(), self.height() + item.height())
        item.startAnimation(pos, 0.0, self._duration, QEasingCurve.Type.InOutQuad,
                            True, onFinished=item.deleteLater)

    def __initWidget(self) -> None:
        self.default()
        self.setFixedSize(self._itemSize.width() + self._margin[0] + self._margin[2],
                          3 * self._itemSize.height() + 2 * self._spacing)

    wheelScrolled = Signal(str)


def getNextHour(current: str, direction: str) -> str:
    current = int(current)
    if direction == "up":
        return str(current + 1).zfill(2) if current < 23 else "00"
    else:
        return str(current - 1).zfill(2) if current > 0 else "23"


def getNextMinute(current: str, direction: str) -> str:
    current = int(current)
    if direction == "up":
        return str(current + 1).zfill(2) if current < 59 else "00"
    else:
        return str(current - 1).zfill(2) if current > 0 else "59"


def getNextSecond(current: str, direction: str) -> str:
    current = int(current)
    if direction == "up":
        return str(current + 1).zfill(2) if current < 59 else "00"
    else:
        return str(current - 1).zfill(2) if current > 0 else "59"


class TimePicker(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hLayout = QHBoxLayout(self)
        self.hourPicker = Picker(["23", "00", "01"], self)
        self.minutePicker = Picker(["59", "00", "01"], self)
        self.secondPicker = Picker(["59", "00", "01"], self)
        self.delimiter1 = TitleLabel(":", self)
        self.delimiter2 = TitleLabel(":", self)

        self.__initWidget()

    def default(self) -> None:
        self.hourPicker.default()
        self.minutePicker.default()
        self.secondPicker.default()

    def getCurrentTime(self) -> str:
        return f"{self.hourPicker.getCurrentSelected()}:" \
               f"{self.minutePicker.getCurrentSelected()}:" \
               f"{self.secondPicker.getCurrentSelected()}"

    def setAcceptWheelEvent(self, accept: bool) -> None:
        self.hourPicker.setAcceptWheelEvent(accept)
        self.minutePicker.setAcceptWheelEvent(accept)
        self.secondPicker.setAcceptWheelEvent(accept)

    def __hourScrolled(self, direction: str) -> None:
        if direction == "up":
            current = self.hourPicker.getBottomItemText()
            self.hourPicker.floatUp(getNextHour(current, direction))
        else:
            current = self.hourPicker.getTopItemText()
            self.hourPicker.floatDown(getNextHour(current, direction))

    def __minuteScrolled(self, direction: str) -> None:
        if direction == "up":
            current = self.minutePicker.getBottomItemText()
            self.minutePicker.floatUp(getNextMinute(current, direction))
        else:
            current = self.minutePicker.getTopItemText()
            self.minutePicker.floatDown(getNextMinute(current, direction))

    def __secondScrolled(self, direction: str) -> None:
        if direction == "up":
            current = self.secondPicker.getBottomItemText()
            self.secondPicker.floatUp(getNextSecond(current, direction))
        else:
            current = self.secondPicker.getTopItemText()
            self.secondPicker.floatDown(getNextSecond(current, direction))

    def __connectSignalToSlot(self):
        self.hourPicker.wheelScrolled.connect(self.__hourScrolled)
        self.minutePicker.wheelScrolled.connect(self.__minuteScrolled)
        self.secondPicker.wheelScrolled.connect(self.__secondScrolled)

    def __initWidget(self):
        font = self.delimiter1.font()
        font.setPointSize(50)
        font.setFamily("Segoe UI")
        self.delimiter1.setFont(font)
        self.delimiter2.setFont(font)
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.hLayout.addWidget(self.hourPicker)
        self.hLayout.addWidget(self.delimiter1)
        self.hLayout.addWidget(self.minutePicker)
        self.hLayout.addWidget(self.delimiter2)
        self.hLayout.addWidget(self.secondPicker)
        self.hLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hLayout.setSpacing(10)
        self.hLayout.setContentsMargins(10, 10, 10, 10)


if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    w = TimePicker()
    w.show()
    sys.exit(app.exec())
