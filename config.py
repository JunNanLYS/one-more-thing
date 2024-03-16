import os
from src.py_qobject import PyQDict, PyQList

__version__ = "0.0.1"
__abspath__ = os.path.abspath(os.path.dirname(__file__))
__project__ = "one-more-thing"


def getDefaultData():
    _list = PyQList()
    defaultData = {
        "name": "No name",
        "icon": "F-CAR",
        "hours": 0.0,
        "uid": "",
        "subItems": _list
    }
    res = PyQDict()
    res.replaceDict(defaultData)
    _list.valueChanged.connect(res.valueChanged)
    return res


# path
logPath = r"./logs"
dataPath = r"./data"
resourcePath = r"./resources"

# current working directory
currentWorkingDirectory = os.getcwd()
projectRootDirectory = os.path.dirname(__file__)
if currentWorkingDirectory != projectRootDirectory:
    print(f"Current working directory is {currentWorkingDirectory}, change to {projectRootDirectory}")
    os.chdir(projectRootDirectory)
else:
    print(f"Current working directory is {currentWorkingDirectory}")

if not os.path.exists(dataPath):
    os.makedirs(dataPath)
if not os.path.exists(logPath):
    os.makedirs(logPath)
if not os.path.exists(resourcePath):
    raise FileNotFoundError(f"Resource path {resourcePath} not found")
