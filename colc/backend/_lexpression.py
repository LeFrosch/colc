import enum

from colc.frontend import Quantifier, Comparison, Aggregator


class LFunction(enum.IntEnum):
    WITH = 0
    ATTR = 1
    ALL = 2
    ANY = 3
    ONE = 4
    EQUAL = 5
    NOT_EQUAL = 6
    LESS = 7
    LESS_EQUAL = 8
    GREATER = 9
    GREATER_EQUAL = 10
    MULTIPLE = 11
    POWER = 12
    LIST_SIZE = 13
    LIST_MIN = 14
    LIST_MAX = 15
    LIST_SUM = 16
    LIST_AVG = 17

    def __repr__(self):
        return self.name

    @staticmethod
    def from_quantifier(quantifier: Quantifier) -> 'LFunction':
        return quantifier.switch(
            {
                Quantifier.ALL: LFunction.ALL,
                Quantifier.ANY: LFunction.ANY,
                Quantifier.ONE: LFunction.ONE,
            }
        )

    @staticmethod
    def from_comparison(comparison: Comparison) -> 'LFunction':
        return comparison.switch(
            {
                Comparison.EQL: LFunction.EQUAL,
                Comparison.NEQ: LFunction.NOT_EQUAL,
                Comparison.LES: LFunction.LESS,
                Comparison.LEQ: LFunction.LESS_EQUAL,
                Comparison.GRE: LFunction.GREATER,
                Comparison.GEQ: LFunction.GREATER_EQUAL,
                Comparison.MUT: LFunction.MULTIPLE,
                Comparison.POW: LFunction.POWER,
            }
        )

    @staticmethod
    def from_aggregator(aggregator: Aggregator) -> 'LFunction':
        return aggregator.switch(
            {
                Aggregator.MIN: LFunction.LIST_MIN,
                Aggregator.MAX: LFunction.LIST_MAX,
                Aggregator.SUM: LFunction.LIST_SUM,
                Aggregator.AVG: LFunction.LIST_AVG,
            }
        )


class LExpression:
    def __init__(self, name: LFunction, args: list):
        self.elements = [name, *filter(lambda x: x is not None, args)]

    @property
    def function(self) -> LFunction:
        return self.elements[0]

    @property
    def arguments(self) -> list:
        return self.elements[1:]

    def __repr__(self):
        return f'[{', '.join(repr(e) for e in self.elements)}]'

    def __getstate__(self):
        return self.elements

    def __setstate__(self, state):
        self.elements = state
