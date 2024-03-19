from os.path import isfile, isdir

from qfluentwidgets import FluentIcon

from src.py_qobject import PyQDict, PyQList


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


def pyQDictToDict(_dict: PyQDict) -> dict:
    res = _dict.dict
    for k, v in res.items():
        if isinstance(v, PyQDict):
            v = pyQDictToDict(v)
            res[k] = v
        elif isinstance(v, PyQList):
            v = pyQListToList(v)
            res[k] = v
    return res


def pyQDictToDictCopy(_dict: PyQDict) -> dict:
    res = dict()
    for k, v in _dict.items():
        if isinstance(v, PyQDict):
            v = pyQDictToDictCopy(v)
            res[k] = v
        elif isinstance(v, PyQList):
            v = pyQListToListCopy(v)
            res[k] = v
        else:
            res[k] = v
    return res


def pyQListToList(_list: PyQList) -> list:
    res = _list.list
    i = 0
    while i < len(res):
        v = res[i]
        if isinstance(v, PyQDict):
            v = pyQDictToDict(v)
            res[i] = v
        elif isinstance(v, PyQList):
            v = pyQListToList(v)
            res[i] = v
        i += 1
    return res


def pyQListToListCopy(_list: PyQList) -> list:
    res = list()
    for v in _list:
        if isinstance(v, PyQDict):
            v = pyQDictToDictCopy(v)
            res.append(v)
        elif isinstance(v, PyQList):
            v = pyQListToListCopy(v)
            res.append(v)
        else:
            res.append(v)
    return res


if __name__ == '__main__':
    print(isFluentIconStr(r"F-ADD"))
