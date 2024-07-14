import enum
from typing import Iterable, Optional

from .._internal import internal_problem
from .._utils import flatten

Node = type('NodeKind', tuple(), {})
NodeKind = type('NodeKind', tuple(), {})


class PrimitiveType(enum.StrEnum):
    INTEGER = 'int'
    STRING = 'str'
    BOOLEAN = 'bool'
    NODE = 'node'
    NODE_KIND = 'kind'

    @staticmethod
    def from_python(py_type: Optional[type]) -> 'PrimitiveType':
        if py_type is str:
            return PrimitiveType.STRING
        if py_type is int:
            return PrimitiveType.INTEGER
        if py_type is bool:
            return PrimitiveType.BOOLEAN
        if py_type is Node:
            return PrimitiveType.NODE
        if py_type is NodeKind:
            return PrimitiveType.NODE_KIND

        internal_problem(f'invalid type {py_type}')


class Type:
    values: set[PrimitiveType]
    is_list: bool

    def __init__(self, values: set[PrimitiveType], list: bool = False):
        self.values = values
        self.is_list = list

        # list of none is not allowed
        assert not list or len(values) > 0

    @staticmethod
    def lup(types: Iterable['Type']) -> 'Type':
        """
        Creates the least upper bound of multiple types.
        """

        # TODO: this using list as upper bound for single values is not fully supported
        return Type(
            values=set(flatten(map(lambda it: it.values, types))),
            list=any(map(lambda it: it.is_list, types)),
        )

    @staticmethod
    def from_python(py_type) -> 'Type':
        if py_type is range:
            return Type({PrimitiveType.INTEGER}, list=True)

        return Type({PrimitiveType.from_python(py_type)}, list=False)

    @property
    def is_none(self) -> bool:
        return len(self.values) == 0

    @property
    def is_any(self) -> bool:
        return len(self.values) == len(PrimitiveType)

    @property
    def as_scalar(self) -> 'Type':
        return Type(self.values, list=False)

    def compatible(self, other: 'Type') -> bool:
        if self.is_list != other.is_list:
            return False

        return len(self.values & other.values) > 0

    def __repr__(self):
        if self.is_none:
            type = 'none'
        elif self.is_any:
            type = 'any'
        else:
            # sort for testing
            sorted = list(self.values)
            sorted.sort()

            type = ' | '.join(sorted)

        if self.is_list:
            return '<list %s>' % type
        else:
            return '<%s>' % type
