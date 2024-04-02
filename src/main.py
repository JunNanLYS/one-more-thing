import sys
import time

from PySide6.QtWidgets import QApplication
from qfluentwidgets import (MSFluentWindow, NavigationItemPosition, FluentIcon)

from src.widgets import ProjectIcon
from src.do_thing_interface.do_thing_interface import DoThingInterface
from src.setting_interface.setting_interface import SettingInterface
from src.to_do_list_interface.to_do_list_interface import ToDoListInterface
from src.manager_interface.manager_interface import ManagerInterface
from src.chart_interface.chart_interface import ChartInterface


class View(MSFluentWindow):
    def __init__(self):
        super().__init__()
        self.doThingInterface = DoThingInterface(self)
        self.settingInterface = SettingInterface(self)
        self.toDoListInterface = ToDoListInterface(self)
        self.managerInterface = ManagerInterface(self)
        self.chartInterface = ChartInterface(self)
        self.__initWidget()
        self.__initNavigation()

    def __initNavigation(self):
        self.addSubInterface(
            self.doThingInterface,
            FluentIcon.LABEL,
            "Do thing",
            position=NavigationItemPosition.TOP,
        )

        self.addSubInterface(
            self.toDoListInterface,
            ProjectIcon.TO_DO_LIST,
            "To do list",
            position=NavigationItemPosition.TOP,
        )

        self.addSubInterface(
            self.managerInterface,
            FluentIcon.FOLDER,
            "Manage",
            position=NavigationItemPosition.SCROLL
        )

        self.addSubInterface(
            self.chartInterface,
            FluentIcon.MARKET,
            "Chart",
            position=NavigationItemPosition.SCROLL,
        )

        self.addSubInterface(
            self.settingInterface,
            FluentIcon.SETTING,
            "Setting",
            position=NavigationItemPosition.BOTTOM,
        )

    def __initWidget(self):
        self.setWindowTitle("One more thing")
        self.setMinimumSize(800, 600)
        self.resize(900, 600)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    start = time.time()
    v = View()
    v.show()
    print(time.time() - start)
    sys.exit(app.exec())
