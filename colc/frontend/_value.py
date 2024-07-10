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
    def is_comptime(self) -> bool:
        pass

    @property
    @abc.abstractmethod
    def is_runtime(self) -> bool:
        pass

    def assignable_to(self, other: Type) -> bool:
        return other in self.possible_types

    def __repr__(self):
        if len(self.possible_types) == 0:
            return '<none>'
        if len(self.possible_types) == len(Type):
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
    def is_runtime(self) -> bool:
        return True


class ComptimeValue(Value):
    concrete_type: Type
    comptime: str | int | bool

    def __init__(self, value: str | int | bool):
        self.comptime = value
        self.concrete_type = Type.from_python(type(value))
        self.possible_types = {self.concrete_type}

    @property
    def is_comptime(self) -> bool:
        return True

    @property
    def is_runtime(self) -> bool:
        return False

    def __str__(self):
        return super().__repr__()

    def __repr__(self):
        return '%s: %s' % (self.comptime, super().__repr__())


DefaultValue = RuntimeValue(set(Type))
