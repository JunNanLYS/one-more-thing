import time

from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPaintEvent, QPainter, QImage
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QFrame
from qfluentwidgets import ToolButton, FluentIcon
from qframelesswindow import TitleBarBase

from log import logger
from src.widgets import (TimePicker, getNextHour, getNextMinute, getNextSecond)


class MyWindow(QFrame):
    class TitleBar(TitleBarBase):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.minBtn.hide()
            self.maxBtn.hide()
            self.setDoubleClickEnabled(False)
            self.hLayout = QHBoxLayout(self)
            self.hLayout.addWidget(self.closeBtn, 0, Qt.AlignmentFlag.AlignRight)
            self.hLayout.setContentsMargins(0, 0, 0, 0)

        def mouseMoveEvent(self, e):
            e.ignore()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._backgroundImage = None
        self._backgroundColor = QColor("#e6e6e6")
        self.titleBar = self.TitleBar(self)
        self.titleBar.raise_()
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

    def resizeEvent(self, e) -> None:
        super().resizeEvent(e)
        self.titleBar.resize(self.width(), self.titleBar.height())

    def paintEvent(self, e: QPaintEvent) -> None:
        rect = self.rect()
        painter = QPainter(self)

        painter.setRenderHints(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._backgroundColor)

        painter.drawRect(rect)
        if self._backgroundImage is not None:
            painter.drawImage(rect, self._backgroundImage)

    def setBackgroundColor(self, color: QColor) -> None:
        self._backgroundColor = color
        self.update()

    def setBackgroundImage(self, image: str) -> None:
        image = QImage(image)
        self._backgroundImage = image
        self.update()


class TimeClock(QWidget):
    def __init__(self, parent=None, countDown=False):
        super().__init__(parent)
        self.__hours = 0
        self.__minutes = 0
        self.__seconds = 0
        self.__totalSeconds = 0
        self._countDown = countDown
        self._layout = QVBoxLayout(self)
        self._timer = None
        self.timePicker = TimePicker(self)

        self.__initWidget()

    def isCountDown(self) -> bool:
        return self._countDown

    def pause(self) -> None:
        """Pause the timer"""
        self._timer.stop()
        logger.info(f"Paused at {self.__hours}:{self.__minutes}:{self.__seconds}")

    def resetTimeAttr(self) -> None:
        """Reset the time attributes"""
        self.__hours = 0
        self.__minutes = 0
        self.__seconds = 0
        self.__totalSeconds = 0

    def setCountDown(self, countDown: bool) -> None:
        self._countDown = countDown
        self.timePicker.default()
        self.timePicker.setAcceptWheelEvent(countDown)

    def start(self) -> None:
        """Start the timer"""
        self._timer = QTimer()
        if self._countDown:
            self.__hours = int(self.timePicker.hourPicker.getCurrentSelected())
            self.__minutes = int(self.timePicker.minutePicker.getCurrentSelected())
            self.__seconds = int(self.timePicker.secondPicker.getCurrentSelected())
            self._timer.timeout.connect(self._subSecond)
            self.timePicker.setAcceptWheelEvent(False)
        else:
            self._timer.timeout.connect(self._addSecond)
        self._timer.start(1000)
        logger.info(f"Started at {self.__hours}:{self.__minutes}:{self.__seconds}")

    def stop(self) -> None:
        """Stop the timer"""
        self._timer.stop()
        self.setCountDown(self._countDown)
        self.finished.emit(self.__totalSeconds)
        logger.info(f"Stopped at {self.__hours}:{self.__minutes}:{self.__seconds}")
        self.resetTimeAttr()

    def _addSecond(self) -> None:
        current = self.timePicker.secondPicker.getBottomItemText()
        if self.__seconds < 59:
            self.__seconds += 1
            self.__totalSeconds += 1
            self.timePicker.secondPicker.floatUp(getNextSecond(current, "up"))
        else:
            if self._addMinute():
                self.timePicker.secondPicker.floatUp(getNextSecond(current, "up"))
                self.__seconds = 0
                self.__totalSeconds += 1
            else:
                self.stop()

    def _addMinute(self) -> bool:
        current = self.timePicker.minutePicker.getBottomItemText()
        if self.__minutes < 59:
            self.__minutes += 1
            self.timePicker.minutePicker.floatUp(getNextMinute(current, "up"))
            return True
        else:
            if self._addHour():
                self.timePicker.minutePicker.floatUp(getNextMinute(current, "up"))
                self.__minutes = 0
                return True
            else:
                return False

    def _addHour(self) -> bool:
        current = self.timePicker.hourPicker.getBottomItemText()
        if self.__hours < 23:
            self.__hours += 1
            self.timePicker.hourPicker.floatUp(getNextHour(current, "up"))
            return True
        else:
            return False

    def _subSecond(self) -> None:
        current = self.timePicker.secondPicker.getTopItemText()
        if self.__seconds > 0:
            self.__seconds -= 1
            self.__totalSeconds += 1
            self.timePicker.secondPicker.floatDown(getNextSecond(current, "down"))
        else:
            if self._subMinute():
                self.__seconds = 59
                self.__totalSeconds += 1
                self.timePicker.secondPicker.floatDown(getNextSecond(current, "down"))
            else:
                self.stop()

    def _subMinute(self) -> bool:
        current = self.timePicker.minutePicker.getTopItemText()
        if self.__minutes > 0:
            self.__minutes -= 1
            self.timePicker.minutePicker.floatDown(getNextMinute(current, "down"))
            return True
        else:
            if self._subHour():
                self.__minutes = 59
                self.timePicker.minutePicker.floatDown(getNextMinute(current, "down"))
                return True
            else:
                return False

    def _subHour(self) -> bool:
        current = self.timePicker.hourPicker.getTopItemText()
        if self.__hours > 0:
            self.__hours -= 1
            self.timePicker.hourPicker.floatDown(getNextHour(current, "down"))
            return True
        else:
            return False

    def __initWidget(self):
        self.setCountDown(self._countDown)
        self.__initLayout()

    def __initLayout(self):
        self._layout.addWidget(self.timePicker)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    finished = pyqtSignal(int)  # Signal emit seconds


class CounterPage(QWidget):
    class FullScreenWindow(MyWindow):
        def __init__(self, timeClock: TimeClock, callback):
            super().__init__()
            timeClock.setParent(self)
            timeClock.finished.connect(callback)
            self.callback = callback
            self.vLayout = QVBoxLayout(self)
            self.vLayout.addWidget(timeClock)

            self.titleBar.closeBtn.clicked.disconnect(self.window().close)
            self.titleBar.closeBtn.clicked.connect(callback)
            self.showMaximized()
            self.setBackgroundImage(r"F:\one-more-thing\resources\images\background\3.png")

    def __init__(self, parent=None):
        super().__init__(parent)
        start = time.time()
        logger.debug("---CounterPage initializing---")
        self._mode = "stop"
        self.vLayout = QVBoxLayout(self)
        self.timeClock = TimeClock(self)
        self.fullScreenWindow = None
        self.pauseBt = ToolButton(FluentIcon.PAUSE, self)
        self.startBt = ToolButton(FluentIcon.PLAY, self)
        self.stopBt = ToolButton(FluentIcon.ACCEPT, self)
        self.__initWidget()
        logger.info(f"CounterPage Initialization time: {time.time() - start}")
        logger.debug("---CounterPage initialized---")

    def backToWindow(self) -> None:
        self.fullScreenWindow.hide()
        self.timeClock.setParent(self)
        self.__initLayout()
        self.window().show()

        self.fullScreenWindow.deleteLater()
        self.fullScreenWindow = None
        self.timeClock.finished.disconnect(self.backToWindow)

    def fullScreen(self) -> None:
        self.fullScreenWindow = self.FullScreenWindow(self.timeClock, self.backToWindow)
        self.fullScreenWindow.show()
        self.window().hide()

    def mode(self):
        return self._mode

    def setCountDown(self, countDown: bool) -> None:
        self.timeClock.setCountDown(countDown)

    def setMode(self, mode: str) -> None:
        if mode == "start":
            self.pauseBt.show()
            self.stopBt.show()
            self.startBt.hide()
        elif mode == "pause":
            self.startBt.show()
            self.stopBt.show()
            self.pauseBt.hide()
        elif mode == "stop":
            self.startBt.show()
            self.pauseBt.hide()
            self.stopBt.hide()
        self._mode = mode
        self.modeChanged.emit(mode)

    def __connectSignalToSlot(self) -> None:
        self.startBt.clicked.connect(self.timeClock.start)
        self.startBt.clicked.connect(lambda: self.setMode("start"))
        self.pauseBt.clicked.connect(self.timeClock.pause)
        self.pauseBt.clicked.connect(lambda: self.setMode("pause"))
        self.stopBt.clicked.connect(self.timeClock.stop)
        self.stopBt.clicked.connect(lambda: self.setMode("stop"))

        self.timeClock.finished.connect(lambda: self.setMode("stop"))
        self.timeClock.finished.connect(lambda x: logger.info(f"Total seconds: {x}"))

    def __initWidget(self) -> None:
        self.setMode("stop")
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self) -> None:
        bottomLayout = QHBoxLayout()
        bottomLayout.addWidget(self.stopBt)
        bottomLayout.addWidget(self.pauseBt)
        bottomLayout.addWidget(self.startBt)

        self.vLayout.addWidget(self.timeClock)
        self.vLayout.addLayout(bottomLayout)
        self.vLayout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

    modeChanged = pyqtSignal(str)  # Signal emit mode


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    win = CounterPage()
    win.resize(500, 500)
    win.show()
    sys.exit(app.exec())
