import enum

from types import UnionType
from typing import Iterable, Optional, get_args, get_origin

from colc.common import first

from .._internal import internal_problem
from .._utils import flatten


class Node: ...


class NodeKind(str): ...


num = int | float

comptime_data = num | str | bool | NodeKind | None
comptime_list = list[comptime_data]
comptime = comptime_list | comptime_data


class PrimitiveType(enum.StrEnum):
    NONE = 'none'
    NUMBER = 'num'
    STRING = 'str'
    BOOLEAN = 'bool'
    NODE = 'node'
    NODE_KIND = 'kind'

    @staticmethod
    def from_python(py_type: Optional[type]) -> 'PrimitiveType':
        if py_type is None or py_type is type(None):
            return PrimitiveType.NONE
        if py_type is str:
            return PrimitiveType.STRING
        if py_type is num or py_type is int or py_type is float:
            return PrimitiveType.NUMBER
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
        if get_origin(py_type) is list:
            py_type = first(get_args(py_type))
            is_list = True
        else:
            is_list = False

        if isinstance(py_type, UnionType):
            types = set(map(lambda it: PrimitiveType.from_python(it), get_args(py_type)))
        else:
            types = {PrimitiveType.from_python(py_type)}

        return Type(types, list=is_list)

    @property
    def is_any(self) -> bool:
        return len(self.values) == len(PrimitiveType)

    @property
    def is_void(self) -> bool:
        return len(self.values) == 0

    @property
    def as_scalar(self) -> 'Type':
        return Type(self.values, list=False)

    @property
    def as_list(self) -> 'Type':
        return Type(self.values, list=True)

    def compatible(self, other: 'Type') -> bool:
        if self.is_list != other.is_list:
            return False

        return len(self.values & other.values) > 0

    def __repr__(self):
        if self.is_any:
            type = 'any'
        elif self.is_void:
            type = 'void'
        else:
            # sort for testing
            sorted = list(self.values)
            sorted.sort()

            type = ' | '.join(sorted)

        if self.is_list:
            return '<list %s>' % type
        else:
            return '<%s>' % type

    def __eq__(self, other) -> bool:
        if not isinstance(other, Type):
            return False
        if self.is_list != other.is_list:
            return False

        return self.values == other.values
