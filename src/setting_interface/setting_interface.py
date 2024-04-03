import os.path

from PySide6.QtCore import Qt, QEasingCurve
from PySide6.QtWidgets import QWidget, QFileDialog
from qfluentwidgets import (SettingCardGroup, SmoothScrollArea, ExpandLayout,
                            PushSettingCard, FluentIcon, TitleLabel,
                            SwitchSettingCard, ComboBoxSettingCard,
                            OptionsSettingCard, setTheme)

import config as cfg
from src.utils.file import getFilename

ds = cfg.cfgDS


class SettingInterface(SmoothScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLb = TitleLabel("Settings", self)
        self.scrollWidget = QWidget(self)
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # do thing
        self.doThingGroup = SettingCardGroup("Do Thing", self.scrollWidget)
        self.clockBackgroundImage = PushSettingCard(
            title="Clock background image",
            icon=FluentIcon.FOLDER,
            content=getFilename(ds.get(ds.clockBackgroundImage)),
            text="Set",
            parent=self.doThingGroup
        )
        self.usePomodoroTime = SwitchSettingCard(
            title="Enable Pomodoro time",
            icon=FluentIcon.STOP_WATCH,
            configItem=ds.usePomodoroTime,
            parent=self.doThingGroup
        )
        self.onePomodoroTime = OptionsSettingCard(
            title="One Pomodoro time",
            icon=FluentIcon.STOP_WATCH,
            content="Set your one Pomodoro time",
            configItem=ds.onePomodoroTime,
            texts=["15", "20", "25", "30"],
            parent=self.doThingGroup
        )
        self.pomodoroBreak = OptionsSettingCard(
            title="Pomodoro break",
            icon=FluentIcon.STOP_WATCH,
            content="Set your break time",
            configItem=ds.pomodoroBreak,
            texts=["0", "5", "10"],
            parent=self.doThingGroup
        )
        self.afterFourPomodoro = OptionsSettingCard(
            title="After four Pomodoro time",
            icon=FluentIcon.STOP_WATCH,
            content="Set your break time",
            configItem=ds.afterFourPomodoro,
            texts=["10", "15", "20", "25", "30"],
            parent=self.doThingGroup
        )
        # do thing end

        # log
        self.logGroup = SettingCardGroup("Log", self.scrollWidget)
        self.outputLog = SwitchSettingCard(
            title="Output log",
            icon=FluentIcon.VIEW,
            content="Use log",
            configItem=ds.outputLog,
            parent=self.logGroup
        )
        self.logPath = PushSettingCard(
            title="Log path",
            icon=FluentIcon.FOLDER,
            content=os.path.abspath(ds.get(ds.logPath)),
            text="Set",
            parent=self.logGroup
        )
        self.logLevel = ComboBoxSettingCard(
            title="Log level",
            icon=FluentIcon.DICTIONARY,
            content="Set you log level",
            configItem=ds.logLevel,
            texts=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            parent=self.logGroup
        )
        # log end

        # personalization
        self.personalizationGroup = SettingCardGroup("Personalization", self.scrollWidget)
        self.applicationTheme = OptionsSettingCard(
            title="Application theme",
            icon=FluentIcon.BRUSH,
            content="Set your application theme",
            configItem=ds.themeMode,
            texts=["Light", "Dark", "Auto"],
            parent=self.personalizationGroup
        )
        self.language = ComboBoxSettingCard(
            title="Language",
            icon=FluentIcon.LANGUAGE,
            content="Set you language for UI",
            configItem=ds.language,
            texts=["English", "简体中文"],
            parent=self.personalizationGroup
        )
        self.useOpenGL = SwitchSettingCard(
            title="Hardware acceleration",
            icon=FluentIcon.VIEW,
            content="Enable hardware acceleration",
            configItem=ds.useOpenGL,
            parent=self.personalizationGroup
        )
        # personalization end

        self._setQss()
        self.__initWidget()

    def _setQss(self):
        self.setStyleSheet("QScrollArea{background: transparent; border: none;}")
        self.scrollWidget.setStyleSheet("QWidget{background: transparent;}")

    def __onClockBICardClicked(self):
        dialog = QFileDialog(self.window())
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setNameFilter("Images (*.png *.jpg *.jpeg)")
        dialog.setViewMode(QFileDialog.ViewMode.List)
        dialog.setDirectory(os.path.dirname(os.path.abspath(ds.get(ds.clockBackgroundImage))))

        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            path = dialog.selectedFiles()[0]
            self.clockBackgroundImage.setContent(getFilename(path))
            ds.set(ds.clockBackgroundImage, path)

    def __onLogPathCardClicked(self):
        dialog = QFileDialog(self.window())
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setViewMode(QFileDialog.ViewMode.List)
        dialog.setDirectory(os.path.abspath(ds.get(ds.logPath)))

        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            path = dialog.selectedFiles()[0]
            self.logPath.setContent(path)
            ds.set(ds.logPath, path)

    def __connectSignal(self):
        self.clockBackgroundImage.clicked.connect(self.__onClockBICardClicked)
        self.logPath.clicked.connect(self.__onLogPathCardClicked)
        self.applicationTheme.optionChanged.connect(lambda item: setTheme(item.value))

    def __initWidget(self):
        self.setObjectName("SettingInterface")
        self.scrollWidget.setObjectName("scrollWidget")
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setScrollAnimation(Qt.Orientation.Vertical, 400, QEasingCurve.OutQuint)
        self.setScrollAnimation(Qt.Orientation.Horizontal, 400, QEasingCurve.OutQuint)
        self.setViewportMargins(0, 80, 0, 20)
        self.__initSettingGroup()
        self.__initLayout()
        self.__connectSignal()

    def __initSettingGroup(self):
        self.doThingGroup.addSettingCard(self.clockBackgroundImage)
        self.doThingGroup.addSettingCard(self.usePomodoroTime)
        self.doThingGroup.addSettingCard(self.onePomodoroTime)
        self.doThingGroup.addSettingCard(self.pomodoroBreak)
        self.doThingGroup.addSettingCard(self.afterFourPomodoro)

        self.logGroup.addSettingCard(self.outputLog)
        self.logGroup.addSettingCard(self.logPath)
        self.logGroup.addSettingCard(self.logLevel)

        self.personalizationGroup.addSettingCard(self.applicationTheme)
        self.personalizationGroup.addSettingCard(self.language)
        self.personalizationGroup.addSettingCard(self.useOpenGL)

    def __initLayout(self):
        self.titleLb.move(36, 30)
        self.expandLayout.addWidget(self.doThingGroup)
        self.expandLayout.addWidget(self.logGroup)
        self.expandLayout.addWidget(self.personalizationGroup)

        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    v = SettingInterface()
    v.show()
    sys.exit(app.exec())
