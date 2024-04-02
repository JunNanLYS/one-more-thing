import sys
from typing import Callable, Optional

from PySide6.QtCore import QUrl, QObject
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtWidgets import QApplication, QWidget

PlaybackState = QMediaPlayer.PlaybackState


class Music(QObject):
    def __init__(self, path: QUrl):
        super().__init__()
        self._callable: Optional[Callable[[PlaybackState], None]] = None
        self._player = QMediaPlayer(self)
        self._audioOutput = QAudioOutput(parent=self._player)  # 不能实例化为临时变量，否则被自动回收导致无法播放
        self._player.setAudioOutput(self._audioOutput)

        self._player.setSource(path)
        self._audioOutput.setVolume(1)

        self._player.playbackStateChanged.connect(self.__onMusicStateChanged)

    def setMusic(self, path: QUrl) -> None:
        self._player.setSource(path)

    def setStateChangedSlot(self, _callable: Callable[[PlaybackState], None]) -> None:
        self._callable = _callable

    def pause(self) -> None:
        self._player.pause()

    def play(self) -> None:
        self._player.play()

    def stop(self) -> None:
        self._player.stop()

    def __onMusicStateChanged(self, state: PlaybackState) -> None:
        if self._callable is None:
            return
        self._callable(state)


class MusicPlayer(QWidget):
    def __init__(self, path: QUrl, parent=None):
        super().__init__(parent)
        self.music = Music(path)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    musicPlayer = MusicPlayer(QUrl().fromLocalFile(r"F:\one-more-thing\resources\music\alarm clock\1.mp3"))
    musicPlayer.show()
    musicPlayer.music.play()
    sys.exit(app.exec())
