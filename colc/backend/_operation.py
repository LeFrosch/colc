import dataclasses
import operator
import typing

from colc.common import fatal_problem
from colc.frontend import Operator, Type

from ._typing import type_from_value
from ._instruction import Opcode


@dataclasses.dataclass
class Operation:
    type: Type
    operator: Operator
    opcode: Opcode
    evaluate: typing.Callable

    @staticmethod
    def from_binary_operator(op: Operator, left: typing.Any, right: typing.Any) -> 'Operation':
        type = type_from_value(left)
        type_other = type_from_value(right)

        if type != type_other:
            _undefined_binary_operator(op, type, type_other)

        operation = next(filter(lambda it: it.type == type and it.operator == op, _binary_operations), None)

        if operation is None:
            _undefined_binary_operator(op, type, type)

        return operation


_binary_operations = [
    Operation(Type.INTEGER, Operator.ADD, Opcode.I_ADD, operator.add),
    Operation(Type.INTEGER, Operator.SUB, Opcode.I_SUB, operator.sub),
    Operation(Type.INTEGER, Operator.MUL, Opcode.I_MUL, operator.mul),
    Operation(Type.INTEGER, Operator.DIV, Opcode.I_DIV, operator.truediv),
    Operation(Type.STRING, Operator.ADD, Opcode.S_CONCAT, operator.concat),
]

_unary_operations = [
    Operation(Type.INTEGER, Operator.SUB, Opcode.I_NEG, operator.neg),
]


def _undefined_binary_operator(op: Operator, left: Type, right: Type) -> typing.NoReturn:
    fatal_problem(f'undefined operator <{left}> {op.value} <{right}>', op)
