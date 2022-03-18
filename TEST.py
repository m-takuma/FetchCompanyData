

import datetime
from enum import Enum, auto
from mimetypes import init
from traceback import print_tb
from types import NoneType
from dateutil import relativedelta
import jaconv
import json

class Test:
    a = 1
    b = {"a":1}
    def __init__(self) -> None:
        print(len(self.b))
        self.b = 3
    
    def test(self):
        self.a = None

a = [
    1,
    2,
    3,
    4,
    5,
]
test = Test()
print(a)
