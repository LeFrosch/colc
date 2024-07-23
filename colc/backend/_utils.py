from typing import TypeVar, Generic, Optional

from colc.common import fatal_problem, Type, Value
from colc.frontend import ast

from ._scope import Definition
from ._functions import Function

T = TypeVar('T')


class Allocator:
    def __init__(self):
        self.index: int = 0

    def alloc(self) -> int:
        self.index += 1
        return self.index - 1


class Pool(Generic[T]):
    def __init__(self):
        self._items: list[T] = []

    def __iter__(self):
        return self._items.__iter__()

    def intern(self, value: T) -> int:
        if value in self._items:
            return self._items.index(value)
        else:
            self._items.append(value)
            return len(self._items) - 1

    def lookup(self, value: T) -> Optional[int]:
        if value in self._items:
            return self._items.index(value)
        else:
            return None


def check_arguments(call: ast.Call, func: Function):
    if len(call.arguments) != len(func.parameters):
        fatal_problem(f'expected {len(func.parameters)} arguments', call)


def check_compatible(expr: ast.Expression, value: Value, type: Type):
    if not value.type.compatible(type):
        fatal_problem(f'expression {value} not compatible with {type}', expr)


def check_assignment(identifier: ast.Identifier, definition: Definition, type: Type):
    if definition.final:
        fatal_problem('cannot assign to final identifier', identifier)
    if type.is_void:
        fatal_problem('cannot assign void', identifier)
