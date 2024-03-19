import os

from qfluentwidgets import (QConfig, ConfigItem, OptionsConfigItem, OptionsValidator,
                            qconfig)

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
configPath = r"./config.json"
dataPath = r"./data"
logPath = r"./logs"
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


class Config(QConfig):
    """Config of application"""
    outputLog = ConfigItem("log", "output", False)
    logLevel = OptionsConfigItem("log", "level", "DEBUG", OptionsValidator([
        "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
    ]))
    logPath = ConfigItem("log", "path", logPath)

    clockBackgroundImage = ConfigItem("counterPage", "backgroundImage",
                                      os.path.join(resourcePath, "images", "background", "3"))


# config data storge
cfgDS = Config()
qconfig.load(configPath, cfgDS)
if not os.path.exists(configPath):
    cfgDS.save()
cfgDS.set(cfgDS.outputLog, False)
