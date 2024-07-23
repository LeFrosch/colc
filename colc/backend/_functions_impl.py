# mypy: ignore-errors

from colc.common import Node, NodeKind, num, comptime_data
from colc.frontend import Operator

from ._functions import builtin
from ._opcode import Opcode

any = comptime_data | Node


@builtin(Operator.CONCAT, Opcode.CONCAT)
def concat_str(left: str, right: str) -> str:
    return left + right


@builtin(Operator.ADD, Opcode.ADD)
def add_int(left: num, right: num) -> num:
    return left + right


@builtin(Operator.SUB, Opcode.SUB)
def sub_int(left: num, right: num) -> num:
    return left - right


@builtin(Operator.DIV, Opcode.DIV)
def div_int(left: num, right: num) -> float:
    return float(left) / float(right)


@builtin(Operator.DIV_FLOOR, Opcode.DIV_FLOOR)
def div_floor_int(left: num, right: num) -> num:
    return left // right


@builtin(Operator.MUL, Opcode.MUL)
def mul_int(left: num, right: num) -> num:
    return left * right


@builtin(Operator.EQL, Opcode.EQL)
def eql_any(left: any, right: any) -> bool:
    if type(left) is not type(right):
        return False

    return left == right


@builtin(Operator.NEQ, Opcode.NEQ)
def neq_any(left: any, right: any) -> bool:
    return not eql_any(left, right)


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
def neg_int(value: num) -> num:
    return -value


@builtin(Operator.PREPEND, Opcode.PREPEND)
def prepend_impl(item: any, value: list[any]) -> list[any]:
    return None


@builtin('range', Opcode.RANGE)
def range_impl(start: num, end: num) -> list[num]:
    return None


@builtin('kind', Opcode.KIND_OF)
def kind_impl(node: Node) -> NodeKind:
    return None


@builtin('where', Opcode.WHERE)
def where_impl(node: Node, kind: NodeKind) -> list[Node]:
    return None


@builtin('len', Opcode.LENGTH)
def len_impl(value: list[any]) -> int:
    return None


@builtin('str', Opcode.STR_OF)
def str_impl(value: any) -> str:
    # pythons true and false is uppercase
    if value is True:
        return 'true'
    if value is False:
        return 'false'

    return str(value)


@builtin('exec', Opcode.EXEC)
def exec_impl(command: str, core: Node, resources: list[Node]):
    return None


@builtin('children', Opcode.CHILDREN)
def children_impl(node: Node) -> list[Node]:
    return None
