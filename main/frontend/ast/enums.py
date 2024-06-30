import enum
import typing
import lark

import problems


class ASTEnum(enum.Enum):
    def switch[T](self, cases: dict['ASTEnum', T]) -> T:
        return cases[self]

    @classmethod
    def from_token(cls, token: lark.Token) -> typing.Self:
        for element in cls:
            if element.value == token:
                return element

        problems.report_internal(f'unknown element in {cls.__name__}: {token}')


class Comparison(ASTEnum):
    EQUAL = '=='
    NOT_EQUAL = '!='
    LESS = '<'
    LESS_EQUAL = '<='
    GREATER = '>'
    GREATER_EQUAL = '>='
    MULTIPLE = '*='
    POWER = '**='


class Operator(ASTEnum):
    PLUS = '+'
    MINUS = '-'
    MULTIPLICATION = '*'
    DIVISION = '/'


class Quantifier(ASTEnum):
    ALL = 'all:'
    ANY = 'any:'
    ONE = 'one:'


class Aggregator(ASTEnum):
    MIN = 'min'
    MAX = 'max'
    SUM = 'sum'
    AVG = 'avg'
