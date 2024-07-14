from colc.common import fatal_problem, Type, Value
from colc.frontend import ast

from ._scope import Definition
from ._functions import Function


class Allocator:
    def __init__(self):
        self.index: int = 0

    def alloc(self) -> int:
        self.index += 1
        return self.index - 1


def check_arguments(call: ast.Call, func: Function):
    if len(call.arguments) != len(func.parameters):
        fatal_problem(f'expected {len(func.parameters)} arguments', call)


def check_compatible(expr: ast.Expression, value: Value, type: Type):
    if not value.type.compatible(type):
        fatal_problem(f'expression {value} not compatible with {type}', expr)


def check_assignment(identifier: ast.Identifier, definition: Definition, type: Type):
    if definition.final:
        fatal_problem('cannot assign to final identifier', identifier)
    if not definition.value.type.compatible(type):
        fatal_problem(f'cannot assign {type} to {definition.value} identifier', identifier)
