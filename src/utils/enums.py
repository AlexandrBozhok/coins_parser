from enum import Enum


class ExpireDateAction(str, Enum):
    add = 'add'
    subtract = 'subtract'
    