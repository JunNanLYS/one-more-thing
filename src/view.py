import sys
import time

from PyQt6.QtWidgets import QApplication, QWidget
from qfluentwidgets import (MSFluentWindow, FluentIcon, NavigationItemPosition)

from src.do_thing_interface.do_thing_interface import DoThingInterface


class View(MSFluentWindow):
    def __init__(self):
        super().__init__()
        self.doThingInterface = DoThingInterface(self)
        self.__initWidget()
        self.__initNavigation()

    def __initNavigation(self):
        self.addSubInterface(
            self.doThingInterface,
            FluentIcon.LABEL,
            "Do thing",
            position=NavigationItemPosition.TOP
        )

        settingW = QWidget()
        settingW.setObjectName("Setting")
        self.addSubInterface(
            settingW,
            FluentIcon.SETTING,
            "Setting",
            position=NavigationItemPosition.BOTTOM
        )

    def __initWidget(self):
        self.setWindowTitle("One more thing")
        self.setMinimumSize(800, 600)
        self.resize(900, 700)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    start = time.time()
    v = View()
    v.show()
    print(time.time() - start)
    sys.exit(app.exec())
