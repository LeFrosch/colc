import enum
import typing
import lark

from colc.common import internal_problem


class Enum(enum.Enum):
    def switch[T](self, cases: dict[typing.Self, T]) -> T:
        return cases[self]

    @classmethod
    def from_token(cls, token: lark.Token) -> typing.Self:
        for element in cls:
            if element.value == token:
                return element

        internal_problem(f'unknown element in {cls.__name__}: {token}')


class Comparison(Enum):
    EQUAL = '=='
    NOT_EQUAL = '!='
    LESS = '<'
    LESS_EQUAL = '<='
    GREATER = '>'
    GREATER_EQUAL = '>='
    MULTIPLE = '*='
    POWER = '**='


class Operator(Enum):
    PLUS = '+'
    MINUS = '-'
    MULTIPLICATION = '*'
    DIVISION = '/'


class Quantifier(Enum):
    ALL = 'all:'
    ANY = 'any:'
    ONE = 'one:'


class Aggregator(Enum):
    MIN = 'min'
    MAX = 'max'
    SUM = 'sum'
    AVG = 'avg'


class Type(Enum):
    STRING = 'str'
    INTEGER = 'int'
