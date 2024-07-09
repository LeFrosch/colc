import enum
import abc
from typing import Optional

from colc.common import internal_problem


class Type(enum.StrEnum):
    INTEGER = 'int'
    STRING = 'str'
    NODE = 'node'


class Value(abc.ABC):
    type_hint: Optional[Type]

    @property
    @abc.abstractmethod
    def is_comptime(self) -> bool:
        pass

    @property
    @abc.abstractmethod
    def is_runtime(self) -> bool:
        pass


class RuntimeValue(Value):
    def __init__(self, type_hint: Optional[Type] = None):
        self.type_hint = type_hint

    @property
    def is_comptime(self) -> bool:
        return False

    @property
    def is_runtime(self) -> bool:
        return True


class ComptimeValue(Value):
    type_hint: Type
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

    @property
    def is_runtime(self) -> bool:
        return False


DefaultValue = RuntimeValue()
