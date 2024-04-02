import os.path
import time
from typing import Optional

from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtCore import QTimer, Qt, Signal, QObject, QUrl
from PySide6.QtGui import QColor, QPaintEvent, QPainter, QImage
from PySide6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QFrame, QSpacerItem, QSizePolicy
from qfluentwidgets import (ToolButton, FluentIcon, SwitchButton, StateToolTip, BodyLabel)
from qframelesswindow import TitleBarBase

import config as cfg
from config import cfgDS
from log import logger
from src.py_qobject import PyQDict
from src.widgets import (TimePicker, getNextHour, getNextMinute, getNextSecond, Music, TimerLabel)

PlaybackState = QMediaPlayer.PlaybackState
dataStorage = cfgDS


class PomodoroTime(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dataStorage = dataStorage
        self.isBreakTime = False
        self.count = 0
        self.dataStorage.usePomodoroTime.valueChanged.connect(self.enableChanged)
        self.dataStorage.onePomodoroTime.valueChanged.connect(self.onePomodoroTimeChanged)

    @property
    def isFourTime(self) -> bool:
        return self.count % 4 == 0

    @property
    def isEnabled(self) -> bool:
        return self.dataStorage.usePomodoroTime.value

    @property
    def oneTime(self) -> int:
        return self.dataStorage.onePomodoroTime.value

    @property
    def oneTimeBreak(self) -> int:
        return self.dataStorage.pomodoroBreak.value

    @property
    def fourTimeBreak(self) -> int:
        return self.dataStorage.afterFourPomodoro.value

    enableChanged = Signal(object)
    onePomodoroTimeChanged = Signal(object)


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
        self.preSeconds = 0
        self.timePicker = TimePicker(self)
        self.finished.connect(lambda s: logger.info(f"Total seconds: {s}"))

        self.__initWidget()

    def isCountDown(self) -> bool:
        return self._countDown

    def isRunning(self) -> bool:
        if self._timer is None:
            return False
        return self._timer.isActive()

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

    def setHour(self, hour: int | str) -> None:
        self.timePicker.setHour(hour)

    def setMinute(self, minute: int | str) -> None:
        self.timePicker.setMinute(minute)

    def setSecond(self, second: int | str) -> None:
        self.timePicker.setSecond(second)

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
        temp = self.__totalSeconds
        self.resetTimeAttr()
        self.preSeconds = temp
        logger.info(f"Stopped at {self.__hours}:{self.__minutes}:{temp}")
        self.finished.emit(temp)

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
            self.setBackgroundImage(dataStorage.clockBackgroundImage.value)

    def __init__(self, parent=None):
        super().__init__(parent)
        start = time.time()
        logger.debug("---CounterPage initializing---")
        # flag
        self.__earlyStop = False

        # data
        self._dict: Optional[PyQDict] = None
        self.music = Music(QUrl().fromLocalFile(os.path.join(
            cfg.resourcePath,
            "music",
            "alarm clock",
            "1.mp3"
        )))
        self.pomodoroTime = PomodoroTime(self)

        # widget
        self.vLayout = QVBoxLayout(self)
        self.timeClock = TimeClock(self)
        self.fullScreenWindow = None
        self.backBt = ToolButton(FluentIcon.RETURN, self)
        self.countDownBt = SwitchButton(self)
        self.fullScreenBt = ToolButton(FluentIcon.FULL_SCREEN, self)
        self.pauseBt = ToolButton(FluentIcon.PAUSE, self)
        self.startBt = ToolButton(FluentIcon.PLAY, self)
        self.stopBt = ToolButton(FluentIcon.ACCEPT, self)
        self.breakTimer = TimerLabel(self)
        self.pomodoroBreakLabel = BodyLabel("Pomodoro break time", self)
        self.stateToolTip: Optional[StateToolTip] = None
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

    def playMusic(self):
        if not self.countDownBt.isChecked():
            return
        self.music.play()
        self.stateToolTip = StateToolTip(
            title="Playing music",
            content="timeout",
            parent=self.window()
        )
        self.stateToolTip.move(self.stateToolTip.getSuitablePos())
        self.stateToolTip.closedSignal.connect(self.music.stop)
        self.music.setStateChangedSlot(
            lambda state: self.stateToolTip.close() if state == PlaybackState.StoppedState else ...)
        self.stateToolTip.show()

    def setDict(self, _dict: PyQDict) -> None:
        self._dict = _dict

    def updateData(self, seconds: int) -> None:
        if self._dict is None:
            logger.error("No data")
        res = round(seconds / 3600, 2)
        self._dict["hours"] += res
        logger.info(f"name: {self._dict['name']}, hours: {self._dict['hours']}")

    def _onStart(self) -> None:
        self.__earlyStop = False
        self._setControllerState(1)
        self._setBottomState(0)
        pomodoro = self.pomodoroTime
        if pomodoro.isEnabled:
            pass
        else:
            pass
        self.backBt.setEnabled(False)
        self.countDownBt.setEnabled(False)
        self.timeClock.start()
        self.breakTimer.pause()

    def _onPause(self) -> None:
        self._setControllerState(2)
        self._setBottomState(1)
        self.breakTimer.start()
        self.timeClock.pause()

    def _onStop(self) -> None:
        self.__earlyStop = True
        self._setControllerState(0)
        self._setBottomState(0)
        self.timeClock.stop()
        self.updateData(self.timeClock.preSeconds)
        self.breakTimer.stop()
        pomodoro = self.pomodoroTime
        if pomodoro.isEnabled:
            self.timeClock.setMinute(self.pomodoroTime.oneTime)
        else:
            self.countDownBt.setEnabled(True)
        self.backBt.setEnabled(True)

    def _onFinished(self, seconds: int) -> None:
        if self.__earlyStop:
            return
        self._setControllerState(0)
        self.breakTimer.stop()
        pomodoro = self.pomodoroTime
        if pomodoro.isEnabled:
            pomodoro.isBreakTime = not pomodoro.isBreakTime
            pomodoro.count += 1
            if pomodoro.isBreakTime:
                self._setControllerState(3)
                self._setBottomState(2)
                oneTimeBreak, fourTimeBreak = pomodoro.oneTimeBreak, pomodoro.fourTimeBreak
                isFourTime = pomodoro.isFourTime
                self.timeClock.setMinute(oneTimeBreak if not isFourTime else fourTimeBreak)
                self.timeClock.start()
            else:
                self._setBottomState(0)
        else:
            self._setBottomState(0)
            self.countDownBt.setEnabled(True)
        self.backBt.setEnabled(True)
        self.updateData(seconds)

    def _onCountDownChanged(self, checked: bool) -> None:
        if self.timeClock.isRunning():
            return
        self.timeClock.setCountDown(checked)

    def _onPomodoroTimeEnableChanged(self, enable: bool) -> None:
        if enable:
            self.countDownBt.setChecked(True)
            self.countDownBt.setEnabled(False)
            self.timeClock.setCountDown(True)
            self.timeClock.timePicker.setAcceptWheelEvent(False)
            self.timeClock.timePicker.default()
            self.timeClock.setMinute(self.pomodoroTime.oneTime)
        else:
            self.countDownBt.setEnabled(True)
            self.timeClock.setCountDown(self.countDownBt.isChecked())
            self.timeClock.timePicker.default()

    def _onOnePomodoroTimeChanged(self, _time: int) -> None:
        if self.timeClock.isRunning():
            return
        self.timeClock.setMinute(_time)

    def _setControllerState(self, state: int) -> None:
        """ set controller state
        controller: [stop, start, pause]
        0: stop
        1: start
        2: pause
        3: normal
        """
        match state:
            case 0:
                self.pauseBt.hide()
                self.stopBt.hide()
                self.startBt.show()
            case 1:
                self.pauseBt.show()
                self.stopBt.show()
                self.startBt.hide()
            case 2:
                self.pauseBt.hide()
                self.stopBt.show()
                self.startBt.show()
            case 3:
                self.pauseBt.hide()
                self.stopBt.hide()
                self.startBt.hide()

    def _setBottomState(self, state: int) -> None:
        """ set bottom state
        0: normal
        1: pause time
        2: pomodoro break time
        """
        match state:
            case 0:
                self.breakTimer.hide()
                self.pomodoroBreakLabel.hide()
            case 1:
                self.breakTimer.show()
                self.pomodoroBreakLabel.hide()
            case 2:
                self.breakTimer.hide()
                self.pomodoroBreakLabel.show()

    def __connectSignalToSlot(self) -> None:
        self.fullScreenBt.clicked.connect(self.fullScreen)
        self.countDownBt.checkedChanged.connect(self._onCountDownChanged)

        self.startBt.clicked.connect(self._onStart)
        self.pauseBt.clicked.connect(self._onPause)
        self.stopBt.clicked.connect(self._onStop)

        self.timeClock.finished.connect(self.backToWindow)
        self.timeClock.finished.connect(self._onFinished)

        self.pomodoroTime.enableChanged.connect(self._onPomodoroTimeEnableChanged)
        self.pomodoroTime.onePomodoroTimeChanged.connect(self._onOnePomodoroTimeChanged)

    def __initWidget(self) -> None:
        self._setControllerState(0)
        self._setBottomState(0)
        self._onPomodoroTimeEnableChanged(self.pomodoroTime.isEnabled)
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
        bottomLayout.addWidget(self.pomodoroBreakLabel)
        bottomLayout.addWidget(self.breakTimer)
        bottomLayout.setSpacing(10)
        bottomLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.vLayout.addLayout(topLayout)
        self.vLayout.addWidget(self.timeClock, 1)
        self.vLayout.addLayout(controllerLayout)
        self.vLayout.addLayout(bottomLayout)
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
