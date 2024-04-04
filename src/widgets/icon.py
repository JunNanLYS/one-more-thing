from enum import Enum
from typing import Union

from qfluentwidgets import Theme, getIconColor, FluentIconBase


class OMThingIcon(FluentIconBase, Enum):
    AI = "ai"
    BASKETBALL = "basketball"
    BOOK = "book"
    CAT = "cat"
    CHINESE = "chinese"
    COFFEE = "coffee"
    DOCX = "docx"
    DOG = "dog"
    DEBUG = "debug"
    ENGLISH = "english"
    EXERCISE = "exercise"
    FISH = "fish"
    FISHING = "fishing"
    GO_TO_WORK = "go_to_work"
    MATH = "math"
    PPT = "ppt"
    PS = "ps"
    RUNNING = "running"
    WECHAT = "wechat"
    WPS = "wps"
    XLSX = "xlsx"

    @classmethod
    def exists(cls, name: str) -> bool:
        values = [m.value for m in cls.__iter__()]
        return name in values

    def serialization(self) -> str:
        return f"OMT-{self.value}"

    @classmethod
    def deSerialization(cls, s: str) -> Union["OMThingIcon", str]:
        if "OMT" not in s:
            return ""
        name = s.removeprefix("OMT-")
        if not cls.exists(name):
            return ""
        name = name.upper()
        return eval(f"OMThingIcon.{name}")

    def path(self, theme=Theme.AUTO) -> str:
        return f"./resources/images/icons/omt/{getIconColor(theme)}/{self.value}.svg"


class ProjectIcon(FluentIconBase, Enum):
    TO_DO_LIST = "toDoList"

    def path(self, theme=Theme.AUTO) -> str:
        return f"./resources/images/icons/project/{getIconColor(theme)}/{self.value}.svg"


if __name__ == '__main__':
    d = OMThingIcon.GO_TO_WORK.serialization()
    print(d)
    print(OMThingIcon.deSerialization(d))

