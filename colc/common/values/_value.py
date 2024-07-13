import abc

from ._type import Type
from . import _types as types


class Value(abc.ABC):
    type: Type

    @property
    @abc.abstractmethod
    def is_comptime(self) -> bool: ...

    @property
    def is_runtime(self) -> bool:
        return not self.is_comptime

    @property
    @abc.abstractmethod
    def as_runtime(self) -> 'RuntimeValue': ...

    def __repr__(self):
        return self.type.__repr__()


class RuntimeValue(Value):
    def __init__(self, type: Type):
        self.type = type

    @property
    def is_comptime(self) -> bool:
        return False

    @property
    def as_runtime(self) -> 'RuntimeValue':
        return self


ComptimePyType = str | int | bool | None


class ComptimeValue(Value):
    comptime: ComptimePyType

    def __init__(self, value: ComptimePyType, type: Type):
        self.comptime = value
        self.type = type

    @staticmethod
    def from_python(value: ComptimePyType) -> 'ComptimeValue':
        return ComptimeValue(value, Type.from_python(type(value)))

    @property
    def is_comptime(self) -> bool:
        return True

    @property
    def as_runtime(self) -> RuntimeValue:
        return RuntimeValue(self.type)

    def __str__(self):
        return super().__repr__()

    def __repr__(self):
        return '%s: %s' % (self.comptime, super().__repr__())


AnyValue = RuntimeValue(types.ANY)
NoneValue = ComptimeValue(None, types.NONE)
