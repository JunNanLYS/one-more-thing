from enum import Enum

from qfluentwidgets import Theme, getIconColor, FluentIconBase

import config as cfg


class OMThingIcon(FluentIconBase, Enum):

    def path(self, theme=Theme.AUTO) -> str:
        return ""


class ProjectIcon(FluentIconBase, Enum):
    def path(self, theme=Theme.AUTO) -> str:
        return ""


if __name__ == '__main__':
    import os

    print(os.listdir(r"F:\one-more-thing\resources\icons\black"))
