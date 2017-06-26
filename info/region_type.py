from enum import Enum


class RegionType(Enum):
    Unknown = 0

    Global = 1
    Class = 2
    Interface = 3
    Namespace = 4
    Struct = 5

    Function = 10
