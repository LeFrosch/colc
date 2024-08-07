import enum
import lark
from typing import Self, Optional, TypeVar

from colc.common import internal_problem, TextFile, Location

T = TypeVar('T')


class AstEnum(enum.StrEnum):
    location: Location

    def switch(self, cases: dict[Self, T], orelse: Optional[T] = None) -> T:
        if orelse is None:
            return cases[self]
        else:
            return cases.get(self, orelse)

    @classmethod
    def synthetic(cls, value: str, location: Location) -> Self:
        try:
            value = cls.__new__(cls, value)
        except ValueError as e:
            internal_problem(f'unknown element in {cls.__name__}', e)

        value.location = location
        return value

    @classmethod
    def from_token(cls, file: TextFile, token: lark.Token) -> Self:
        return cls.synthetic(token.value, file.location_from_token(token))


class Comparison(AstEnum):
    EQL = '=='
    NEQ = '!='
    LES = '<'
    LEQ = '<='
    GRE = '>'
    GEQ = '>='
    MUT = '*='
    POW = '**='


class Operator(AstEnum):
    ADD = '+'
    SUB = '-'
    MUL = '*'
    DIV = '/'
    DIV_FLOOR = '//'
    AND = '&&'
    OR = '||'
    EQL = '=='
    NEQ = '!='
    LES = '<'
    LEQ = '<='
    GRE = '>'
    GEQ = '>='
    MUT = '*='
    POW = '**='
    NOT = '!'
    CONCAT = '..'
    PREPEND = ':'

    def is_comparison(self) -> bool:
        return self.switch(
            {
                Operator.EQL: True,
                Operator.NEQ: True,
                Operator.LES: True,
                Operator.LEQ: True,
                Operator.GRE: True,
                Operator.GEQ: True,
                Operator.MUT: True,
                Operator.POW: True,
            },
            orelse=False,
        )


class Quantifier(AstEnum):
    ALL = 'all:'
    ANY = 'any:'
    ONE = 'one:'


class Aggregator(AstEnum):
    MIN = 'min'
    MAX = 'max'
    SUM = 'sum'
    AVG = 'avg'


class Qualifier(AstEnum):
    VAR = 'var'
    FINAL = 'final'
    CONST = 'const'

    @property
    def is_var(self):
        return self == Qualifier.VAR

    @property
    def is_final(self):
        return self == Qualifier.FINAL

    @property
    def is_const(self):
        return self == Qualifier.CONST
