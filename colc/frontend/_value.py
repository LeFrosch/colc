import enum
import abc

from colc.common import internal_problem


class Type(enum.StrEnum):
    INTEGER = 'int'
    STRING = 'str'
    BOOLEAN = 'bool'
    NODE = 'node'

    @staticmethod
    def from_python(py_type: type) -> 'Type':
        if py_type is str:
            return Type.STRING
        if py_type is int:
            return Type.INTEGER
        if py_type is bool:
            return Type.BOOLEAN

        internal_problem(f'invalid type {py_type}')


class Value(abc.ABC):
    possible_types: set[Type]

    @property
    @abc.abstractmethod
    def is_comptime(self) -> bool: ...

    @property
    def is_runtime(self) -> bool:
        return not self.is_comptime

    @property
    @abc.abstractmethod
    def as_runtime(self) -> 'RuntimeValue': ...

    @property
    def is_none(self) -> bool:
        return len(self.possible_types) == 0

    @property
    def is_any(self) -> bool:
        return len(self.possible_types) == len(Type)

    def assignable_to(self, types: Type | set[Type]) -> bool:
        if isinstance(types, set):
            return len(types & self.possible_types) > 0
        else:
            return types in self.possible_types

    def __repr__(self):
        if self.is_none:
            return '<none>'
        if self.is_any:
            return '<any>'

        # sort for testing
        sorted = list(self.possible_types)
        sorted.sort()

        return '<%s>' % ' | '.join(sorted)


class RuntimeValue(Value):
    def __init__(self, possible_types: set[Type]):
        self.possible_types = possible_types

    @property
    def is_comptime(self) -> bool:
        return False

    @property
    def as_runtime(self) -> 'RuntimeValue':
        return self


ComptimeValueType = str | int | bool | None


class ComptimeValue(Value):
    comptime: ComptimeValueType

    def __init__(self, value: ComptimeValueType):
        self.comptime = value

        if value is None:
            self.possible_types = set()
        else:
            self.possible_types = {Type.from_python(type(value))}

    @property
    def is_comptime(self) -> bool:
        return True

    @property
    def as_runtime(self) -> RuntimeValue:
        return RuntimeValue(self.possible_types)

    def __str__(self):
        return super().__repr__()

    def __repr__(self):
        return '%s: %s' % (self.comptime, super().__repr__())


AnyValue = RuntimeValue(set(Type))
NoneValue = ComptimeValue(None)
