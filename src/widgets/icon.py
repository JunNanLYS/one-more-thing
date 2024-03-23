from enum import Enum

from qfluentwidgets import Theme, getIconColor, FluentIconBase


class OMThingIcon(FluentIconBase, Enum):

    def path(self, theme=Theme.AUTO) -> str:
        return ""


class ProjectIcon(FluentIconBase, Enum):
    TO_DO_LIST = "toDoList"

    def path(self, theme=Theme.AUTO) -> str:
        return f"./resources/images/icons/project/{getIconColor(theme)}/{self.value}.svg"


if __name__ == '__main__':
    import os

    print(os.listdir(r"F:\one-more-thing\resources\icons\black"))
