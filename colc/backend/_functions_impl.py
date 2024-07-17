# mypy: ignore-errors

from colc.common import Node, NodeKind, num
from colc.frontend import Operator

from ._functions import builtin
from ._instruction import Opcode


@builtin(Operator.ADD, Opcode.ADD)
def add_str(left: str, right: str) -> str:
    return left + right


@builtin(Operator.ADD, Opcode.ADD)
def add_int(left: num, right: num) -> int:
    return left + right


@builtin(Operator.SUB, Opcode.SUB)
def sub_int(left: num, right: num) -> int:
    return left - right


@builtin(Operator.DIV, Opcode.DIV)
def div_int(left: num, right: num) -> int:
    # TODO: prefer explicit true div?
    if isinstance(left, int) and isinstance(right, int):
        return left // right
    else:
        return left / right


@builtin(Operator.MUL, Opcode.MUL)
def mul_int(left: num, right: num) -> int:
    return left * right


@builtin(Operator.EQL, Opcode.EQL)
def eql_int(left: num, right: num) -> bool:
    return left == right


@builtin(Operator.EQL, Opcode.EQL)
def eql_str(left: str, right: str) -> bool:
    return left == right


@builtin(Operator.EQL, Opcode.EQL)
def eql_bool(left: bool, right: bool) -> bool:
    return left == right


@builtin(Operator.NEQ, Opcode.NEQ)
def neq_int(left: num, right: num) -> bool:
    return left != right


@builtin(Operator.NEQ, Opcode.NEQ)
def neq_str(left: str, right: str) -> bool:
    return left != right


@builtin(Operator.NEQ, Opcode.NEQ)
def neq_bool(left: bool, right: bool) -> bool:
    return left != right


@builtin(Operator.LES, Opcode.LES)
def les_int(left: num, right: num) -> bool:
    return left < right


@builtin(Operator.LEQ, Opcode.LEQ)
def leq_int(left: num, right: num) -> bool:
    return left <= right


@builtin(Operator.GRE, Opcode.GRE)
def gre_int(left: num, right: num) -> bool:
    return left > right


@builtin(Operator.GEQ, Opcode.GEQ)
def geq_int(left: num, right: num) -> bool:
    return left >= right


@builtin(Operator.MUT, Opcode.MUT)
def mut_int(left: num, right: num) -> bool:
    return left % right == 0


@builtin(Operator.POW, Opcode.POW)
def pow_int(left: num, right: num) -> bool:
    while left % right == 0:
        left = left // right

    return left == 1


@builtin(Operator.OR, Opcode.OR)
def or_bool(left: bool, right: bool) -> bool:
    return left or right


@builtin(Operator.AND, Opcode.AND)
def and_bool(left: bool, right: bool) -> bool:
    return left and right


@builtin(Operator.NOT, Opcode.NOT)
def not_bool(value: bool) -> bool:
    return not value


@builtin(Operator.SUB, Opcode.SUB)
def neg_int(value: num) -> int:
    return -value


@builtin('range', Opcode.RANGE)
def range_impl(start: num, end: num) -> range:
    return None


@builtin('kind', Opcode.KIND)
def kind_impl(node: Node) -> NodeKind:
    return None
