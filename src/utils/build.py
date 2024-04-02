import os
from os import system

cur: str = __file__
while cur.split("\\")[-1] != "one-more-thing":
    cur = os.path.dirname(cur)
os.chdir(cur)
command = "nuitka ./main.py --standalone --remove-output "
command += "--include-data-dir=./data=./data --include-data-dir=./resources=./resources "
command += "--enable-plugin=pyside6 --output-dir=temp/output --mingw64 "
command += "--output-filename=OneMoreThing"
system(command)
