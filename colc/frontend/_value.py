import enum
from typing import Optional

from colc.common import internal_problem


class Type(enum.StrEnum):
    INTEGER = 'int'
    STRING = 'str'
    NODE = 'node'


class Value:
    _default = None

    type_hint: Optional[Type]

    def __init__(self, hint: Optional[Type] = None):
        self.type_hint = hint

    @property
    def is_comptime(self) -> bool:
        return False

    @classmethod
    def default(cls):
        if cls._default is None:
            cls._default = object.__new__(cls)
            cls._default.type_hint = None

        return cls._default


class ComptimeValue(Value):
    comptime: str | int

    def __init__(self, value: str | int):
        self.comptime = value

        if isinstance(value, int):
            self.type_hint = Type.INTEGER
        elif isinstance(value, str):
            self.type_hint = Type.STRING
        else:
            internal_problem(f'not a valid comptime value {value}')

    @property
    def is_comptime(self) -> bool:
        return True

    def __repr__(self):
        return self.comptime.__repr__()

    def __eq__(self, other):
        if isinstance(other, ComptimeValue):
            return self.comptime == other.comptime
        else:
            return False
