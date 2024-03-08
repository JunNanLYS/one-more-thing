import os

__version__ = "0.0.1"
__abspath__ = os.path.abspath(os.path.dirname(__file__))
__project__ = "one-more-thing"

defaultFormat = {
    "name": "No name",
    "icon": "F-CAR",
    "hours": 0.0,
    "uid": "",
    "subItems": []
}

if os.path.exists(os.path.join(__abspath__, "data")):
    os.makedirs(os.path.join(__abspath__, "data"))
if os.path.exists(os.path.join(__abspath__, "logs")):
    os.makedirs(os.path.join(__abspath__, "logs"))
