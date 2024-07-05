import enum
import typing
import lark

from colc.common import internal_problem

T = typing.TypeVar('T')


class AstEnum(enum.StrEnum):
    def switch(self, cases: dict[typing.Self, T]) -> T:
        return cases[self]

    @classmethod
    def from_token(cls, token: lark.Token) -> typing.Self:
        try:
            return cls.__new__(cls, token.value)
        except ValueError as e:
            internal_problem(f'unknown element in {cls.__name__}', e)


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
    PLUS = '+'
    MINUS = '-'
    MULTIPLICATION = '*'
    DIVISION = '/'


class Quantifier(AstEnum):
    ALL = 'all:'
    ANY = 'any:'
    ONE = 'one:'


class Aggregator(AstEnum):
    MIN = 'min'
    MAX = 'max'
    SUM = 'sum'
    AVG = 'avg'


class Type(AstEnum):
    STRING = 'str'
    INTEGER = 'int'
