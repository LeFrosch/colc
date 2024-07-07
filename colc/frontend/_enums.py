import enum
import operator
import typing
import lark

from colc.common import internal_problem, TextFile, Location

T = typing.TypeVar('T')


class AstEnum(enum.StrEnum):
    location: Location

    def switch(self, cases: dict[typing.Self, T]) -> T:
        return cases[self]

    @classmethod
    def from_token(cls, file: TextFile, token: lark.Token) -> typing.Self:
        try:
            value = cls.__new__(cls, token.value)
        except ValueError as e:
            internal_problem(f'unknown element in {cls.__name__}', e)

        value.location = file.location_from_token(token)
        return value


class Comparison(AstEnum):
    EQUAL = '=='
    NOT_EQUAL = '!='
    LESS = '<'
    LESS_EQUAL = '<='
    GREATER = '>'
    GREATER_EQUAL = '>='
    MULTIPLE = '*='
    POWER = '**='


class Operator(AstEnum):
    ADD = '+'
    SUB = '-'
    MUL = '*'
    DIV = '/'

    # TODO: add compile time value type
    def evaluate(self, left, right):
        op = self.switch(
            {
                Operator.ADD: operator.add,
                Operator.SUB: operator.sub,
                Operator.MUL: operator.mul,
                Operator.DIV: operator.truediv,
            }
        )

        return op(left, right)


class Quantifier(AstEnum):
    ALL = 'all:'
    ANY = 'any:'
    ONE = 'one:'


class Aggregator(AstEnum):
    MIN = 'min'
    MAX = 'max'
    SUM = 'sum'
    AVG = 'avg'
