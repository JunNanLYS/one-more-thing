from enum import Enum

from qfluentwidgets import Theme, getIconColor, FluentIconBase

import config as cfg


class OMThingIcon(FluentIconBase, Enum):

    def path(self, theme=Theme.AUTO) -> str:
        return f"{cfg.resourcePath}/icons/{getIconColor(theme)}/{self.value}"


if __name__ == '__main__':
    import os

    print(os.listdir(r"F:\one-more-thing\resources\icons\black"))
