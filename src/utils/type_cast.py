from os.path import isfile, isdir

from qfluentwidgets import FluentIcon


def isFluentIconStr(s: str) -> bool:
    if isfile(s) or isdir(s):
        return False
    elif "F-" not in s:
        return False
    return True


def strToFluentIcon(s: str) -> FluentIcon:
    if not isFluentIconStr(s):
        raise ValueError("Not a FluentIcon string")
    name = s.split('-')[1]
    return eval(f"FluentIcon.{name}")


def fluentIconToStr(icon: FluentIcon) -> str:
    name = icon.name
    return f"F-{name}"


if __name__ == '__main__':
    print(isFluentIconStr(r"F-ADD"))
