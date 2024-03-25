import time
from typing import Optional

from PySide6.QtCore import QTimer, Qt, Signal, QObject
from PySide6.QtGui import QColor, QPaintEvent, QPainter, QImage
from PySide6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QFrame, QSpacerItem, QSizePolicy
from qfluentwidgets import ToolButton, FluentIcon, SwitchButton
from qframelesswindow import TitleBarBase

import config as cfg
from log import logger
from src.py_qobject import PyQDict
from src.widgets import (TimePicker, getNextHour, getNextMinute, getNextSecond)


class PomodoroTime(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        ds = cfg.cfgDS
        self.__enable = ds.get(ds.usePomodoroTime)
        self.__onePomodoroTime = ds.get(ds.onePomodoroTime)
        self.__pomodoroBreak = ds.get(ds.pomodoroBreak)
        self.__afterFourPomodoro = ds.get(ds.afterFourPomodoro)
        self.__connectSignalToSlot()

    def enable(self) -> bool:
        return self.__enable

    def onePomodoroTime(self) -> int:
        return self.__onePomodoroTime

    def pomodoroBreak(self) -> int:
        return self.__pomodoroBreak

    def afterFourPomodoro(self) -> int:
        return self.__afterFourPomodoro

    def __connectSignalToSlot(self):
        ds = cfg.cfgDS
        ds.usePomodoroTime.valueChanged.connect(self.enableChanged)
        ds.onePomodoroTime.valueChanged.connect(self.onePomodoroTimeChanged)
        ds.pomodoroBreak.valueChanged.connect(self.pomodoroBreakChanged)
        ds.afterFourPomodoro.valueChanged.connect(self.afterFourPomodoroChanged)

        self.enableChanged.connect(self.__onEnableChanged)
        self.onePomodoroTimeChanged.connect(self.__onOnePomodoroTimeChanged)
        self.pomodoroBreakChanged.connect(self.__onPomodoroBreakChanged)
        self.afterFourPomodoroChanged.connect(self.__onAfterFourPomodoroChanged)

    def __onEnableChanged(self, enable: bool) -> None:
        self.__enable = enable

    def __onOnePomodoroTimeChanged(self, _time: int) -> None:
        self.__onePomodoroTime = _time

    def __onPomodoroBreakChanged(self, _time: int) -> None:
        self.__pomodoroBreak = _time

    def __onAfterFourPomodoroChanged(self, _time: int) -> None:
        self.__afterFourPomodoro = _time

    enableChanged = Signal(bool)
    onePomodoroTimeChanged = Signal(int)
    pomodoroBreakChanged = Signal(int)
    afterFourPomodoroChanged = Signal(int)


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
        self.finished.connect(lambda s: logger.info(f"Total seconds: {s}"))

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

    finished = Signal(int)  # Signal emit seconds


class CounterPage(QWidget):
    class FullScreenWindow(MyWindow):
        def __init__(self, timeClock: TimeClock, callback):
            super().__init__()
            self.timeClock = timeClock
            self.timeClock.setParent(self)
            self.callback = callback
            self.vLayout = QVBoxLayout(self)
            self.vLayout.addWidget(self.timeClock)

            self.titleBar.closeBtn.clicked.disconnect(self.window().close)
            self.titleBar.closeBtn.clicked.connect(callback)
            self.showMaximized()
            cfgDS = cfg.cfgDS
            self.setBackgroundImage(cfgDS.get(cfgDS.clockBackgroundImage))

    def __init__(self, parent=None):
        super().__init__(parent)
        start = time.time()
        logger.debug("---CounterPage initializing---")
        self._mode = "stop"
        self._dict: Optional[PyQDict] = None
        self.vLayout = QVBoxLayout(self)
        self.timeClock = TimeClock(self)
        self.fullScreenWindow = None
        self.backBt = ToolButton(FluentIcon.RETURN, self)
        self.countDownBt = SwitchButton(self)
        self.fullScreenBt = ToolButton(FluentIcon.FULL_SCREEN, self)
        self.pauseBt = ToolButton(FluentIcon.PAUSE, self)
        self.startBt = ToolButton(FluentIcon.PLAY, self)
        self.stopBt = ToolButton(FluentIcon.ACCEPT, self)
        self.__initWidget()
        logger.info(f"CounterPage Initialization time: {time.time() - start}")
        logger.debug("---CounterPage initialized---")

    def backToWindow(self) -> None:
        if self.fullScreenWindow is None:
            return
        self.fullScreenWindow.hide()
        self.timeClock.setParent(self)
        self.__initLayout()
        self.window().show()

        self.fullScreenWindow.deleteLater()
        self.fullScreenWindow = None

    def fullScreen(self) -> None:
        self.fullScreenWindow = self.FullScreenWindow(self.timeClock, self.backToWindow)
        self.fullScreenWindow.show()
        self.window().hide()

    def mode(self):
        return self._mode

    def setCountDown(self, countDown: bool) -> None:
        self.timeClock.setCountDown(countDown)

    def setDict(self, _dict: PyQDict) -> None:
        self._dict = _dict

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
        isStopped = mode == "stop"
        self.countDownBt.setEnabled(isStopped)
        self.backBt.setEnabled(isStopped)
        self._mode = mode

    def updateData(self, seconds: int) -> None:
        if self._dict is None:
            logger.error("No data")
        res = round(seconds / 3600, 2)
        self._dict["hours"] += res
        logger.info(f"name: {self._dict['name']}, hours: {self._dict['hours']}")

    def __connectSignalToSlot(self) -> None:
        self.fullScreenBt.clicked.connect(self.fullScreen)
        self.countDownBt.checkedChanged.connect(self.setCountDown)

        self.startBt.clicked.connect(self.timeClock.start)
        self.startBt.clicked.connect(lambda: self.setMode("start"))
        self.pauseBt.clicked.connect(self.timeClock.pause)
        self.pauseBt.clicked.connect(lambda: self.setMode("pause"))
        self.stopBt.clicked.connect(self.timeClock.stop)
        self.stopBt.clicked.connect(lambda: self.setMode("stop"))

        self.timeClock.finished.connect(lambda: self.setMode("stop"))
        self.timeClock.finished.connect(self.backToWindow)
        self.timeClock.finished.connect(self.updateData)

    def __initWidget(self) -> None:
        self.setMode("stop")
        self.fullScreenBt.setToolTip("Full Screen")
        self.countDownBt.setOffText("count up")
        self.countDownBt.setOnText("count down")
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self) -> None:
        topLayout = QHBoxLayout()
        topLayout.addWidget(self.backBt)
        topLayout.addItem(QSpacerItem(0, 0, hData=QSizePolicy.Policy.Expanding))
        topLayout.addWidget(self.countDownBt)
        topLayout.addWidget(self.fullScreenBt)
        topLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        controllerLayout = QHBoxLayout()
        controllerLayout.addWidget(self.stopBt)
        controllerLayout.addWidget(self.pauseBt)
        controllerLayout.addWidget(self.startBt)

        bottomLayout = QHBoxLayout()

        self.vLayout.addLayout(topLayout)
        self.vLayout.addWidget(self.timeClock, 1)
        self.vLayout.addLayout(controllerLayout)
        self.vLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vLayout.setContentsMargins(0, 0, 0, 0)
        self.vLayout.setSpacing(10)


if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    win = CounterPage()
    win.resize(500, 500)
    win.show()
    sys.exit(app.exec())
