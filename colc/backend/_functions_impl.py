from colc.frontend import Operator

from ._functions import function


@function(Operator.ADD)
def add_str(left: str, right: str) -> str:
    return left + right


@function(Operator.ADD)
def add_int(left: int, right: int) -> int:
    return left + right


@function(Operator.SUB)
def sub_int(left: int, right: int) -> int:
    return left - right


@function(Operator.DIV)
def div_int(left: int, right: int) -> int:
    return left // right


@function(Operator.MUL)
def mul_int(left: int, right: int) -> int:
    return left * right


@function(Operator.EQL)
def eql_int(left: int, right: int) -> bool:
    return left == right


@function(Operator.EQL)
def eql_str(left: str, right: str) -> bool:
    return left == right


@function(Operator.EQL)
def eql_bool(left: bool, right: bool) -> bool:
    return left == right


@function(Operator.NEQ)
def neq_int(left: int, right: int) -> bool:
    return left != right


@function(Operator.NEQ)
def neq_str(left: str, right: str) -> bool:
    return left != right


@function(Operator.NEQ)
def neq_bool(left: bool, right: bool) -> bool:
    return left != right


@function(Operator.LES)
def les_int(left: int, right: int) -> bool:
    return left < right


@function(Operator.LEQ)
def leq_int(left: int, right: int) -> bool:
    return left <= right


@function(Operator.GRE)
def gre_int(left: int, right: int) -> bool:
    return left > right


@function(Operator.GEQ)
def geq_int(left: int, right: int) -> bool:
    return left >= right


@function(Operator.MUT)
def mut_int(left: int, right: int) -> bool:
    return left % right == 0


@function(Operator.POW)
def pow_int(left: int, right: int) -> bool:
    while left % right == 0:
        left = left // right

    return left == 1


@function(Operator.OR)
def or_bool(left: bool, right: bool) -> bool:
    return left or right


@function(Operator.AND)
def and_bool(left: bool, right: bool) -> bool:
    return left and right


@function(Operator.NOT)
def not_bool(value: bool) -> bool:
    return not value


@function(Operator.SUB)
def neg_int(value: int) -> int:
    return -value
