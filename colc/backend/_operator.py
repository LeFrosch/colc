import operator
from typing import Optional

from colc.common import fatal_problem
from colc.frontend import Operator, Value, RuntimeValue, ComptimeValue, Type

_definitions = {
    Operator.ADD: [Type.INTEGER, Type.STRING],
    Operator.SUB: [Type.INTEGER],
    Operator.MUL: [Type.INTEGER],
    Operator.DIV: [Type.INTEGER],
}


# TODO: move this some where else
def type_check(value: Value, expected: Optional[Type]) -> bool:
    actual = value.type_hint

    # if a type is not known default to true
    if actual is None or expected is None:
        return True

    return actual == expected


def op_type_check(op: Operator, left: Value, right: Value) -> bool:
    # check only if both types are known
    if left.type_hint is None or right.type_hint is None:
        return True

    # for now all operators only work on values of same type
    if left.type_hint != right.type_hint:
        return False

    return left.type_hint in _definitions[op]


def _undefined_operator_problem(op: Operator, left: Value, right: Value):
    fatal_problem(f'undefined operator <{left.type_hint}> {op} <{right.type_hint}>', op)


def op_comptime_evaluate(op: Operator, left: ComptimeValue, right: ComptimeValue) -> ComptimeValue:
    if not op_type_check(op, left, right):
        _undefined_operator_problem(op, left, right)

    op_impl = op.switch(
        {
            Operator.ADD: operator.add,
            Operator.SUB: operator.sub,
            Operator.MUL: operator.mul,
            Operator.DIV: operator.truediv,
        }
    )

    return ComptimeValue(op_impl(left.comptime, right.comptime))


def op_evaluate(op: Operator, left: Value, right: Value) -> Value:
    if not op_type_check(op, left, right):
        _undefined_operator_problem(op, left, right)

    # for now the return type for all operators is equal to the input types
    return RuntimeValue(left.type_hint or right.type_hint)
