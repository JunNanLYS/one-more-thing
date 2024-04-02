import enum

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import QLabel, QHBoxLayout, QWidget

from qfluentwidgets import qconfig, isDarkTheme


class TimerLabel(QWidget):
    class TimerState(enum.Enum):
        STOPPED = 0
        RUNNING = 1
        PAUSED = 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__curState = self.TimerState.STOPPED

        self.hLabel = QLabel("00", self)
        self.mLabel = QLabel("00", self)
        self.sLabel = QLabel("00", self)
        self.delimiter1 = QLabel(":", self)
        self.delimiter2 = QLabel(":", self)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._addSecond)

        self.hLayout = QHBoxLayout(self)
        self.__initWidget()

    def default(self) -> None:
        """ default values for the timer """
        self.hLabel.setText("00")
        self.mLabel.setText("00")
        self.sLabel.setText("00")

    def text(self):
        return f"{self.hLabel.text()}:{self.mLabel.text()}:{self.sLabel.text()}"

    def start(self) -> None:
        if self.__curState == self.TimerState.STOPPED:
            self.default()
        self.timer.start(1000)
        self.__curState = self.TimerState.RUNNING

    def pause(self) -> None:
        self.timer.stop()
        self.__curState = self.TimerState.PAUSED

    def stop(self) -> None:
        self.timer.stop()
        self.stopped.emit()
        self.__curState = self.TimerState.STOPPED
        self.hLabel.setText("00")
        self.mLabel.setText("00")
        self.sLabel.setText("00")

    def _onThemeChanged(self):
        if isDarkTheme():
            self.hLabel.setStyleSheet(f"color: rgb(255, 255, 255);")
            self.mLabel.setStyleSheet(f"color: rgb(255, 255, 255);")
            self.sLabel.setStyleSheet(f"color: rgb(255, 255, 255);")
            self.delimiter1.setStyleSheet(f"color: rgb(255, 255, 255);")
            self.delimiter2.setStyleSheet(f"color: rgb(255, 255, 255);")
        else:
            self.hLabel.setStyleSheet(f"color: rgb(0, 0, 0);")
            self.mLabel.setStyleSheet(f"color: rgb(0, 0, 0);")
            self.sLabel.setStyleSheet(f"color: rgb(0, 0, 0);")
            self.delimiter1.setStyleSheet(f"color: rgb(0, 0, 0);")
            self.delimiter2.setStyleSheet(f"color: rgb(0, 0, 0);")

    def _addSecond(self) -> None:
        seconds = self.sLabel.text()
        if seconds == "59":
            self.sLabel.setText("00")
            self._addMinute()
        else:
            self.sLabel.setText(str(int(seconds) + 1).zfill(2))

    def _addMinute(self) -> None:
        minutes = self.mLabel.text()
        if minutes == "59":
            self.mLabel.setText("00")
            self._addHour()
        else:
            self.mLabel.setText(str(int(minutes) + 1).zfill(2))

    def _addHour(self) -> None:
        hours = self.hLabel.text()
        if hours == "99":
            self.hLabel.setText("00")
        else:
            self.hLabel.setText(str(int(hours) + 1).zfill(2))

    def __connectSignalToSlot(self):
        qconfig.themeChangedFinished.connect(self._onThemeChanged)

    def __initWidget(self):
        font = self.sLabel.font()
        font.setPixelSize(30)
        font.setFamily("Segoe UI")
        self.sLabel.setFont(font)
        self.mLabel.setFont(font)
        self.hLabel.setFont(font)

        font = self.delimiter1.font()
        font.setPixelSize(20)
        font.setFamily("Segoe UI")
        self.delimiter1.setFont(font)
        self.delimiter2.setFont(font)
        self._onThemeChanged()
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.hLayout.addWidget(self.hLabel)
        self.hLayout.addWidget(self.delimiter1)
        self.hLayout.addWidget(self.mLabel)
        self.hLayout.addWidget(self.delimiter2)
        self.hLayout.addWidget(self.sLabel)

        self.hLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hLayout.setContentsMargins(0, 0, 0, 0)
        self.hLayout.setSpacing(5)

    stopped = Signal()


if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    timerLabel = TimerLabel()
    timerLabel.show()
    sys.exit(app.exec())
