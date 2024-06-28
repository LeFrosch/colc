import enum
import operator

from frontend.ast import *


class LFunctions(enum.Enum):
    ALL = 0
    ANY = 1
    ONE = 2
    WITH = 3
    ATTR = 4
    EQUAL = 5
    NOT_EQUAL = 6
    LESS = 7
    LESS_EQUAL = 8
    GREATER = 9
    GREATER_EQUAL = 10
    MULTIPLE = 11
    POWER = 12

    def __repr__(self):
        return self.name

    @staticmethod
    def from_quantifier(quantifier: Quantifier) -> 'LFunctions':
        return quantifier.switch({
            Quantifier.ALL: LFunctions.ALL,
            Quantifier.ANY: LFunctions.ANY,
            Quantifier.ONE: LFunctions.ONE,
        })

    @staticmethod
    def from_comparison(comparison: Comparison) -> 'LFunctions':
        return comparison.switch({
            Comparison.EQUAL: LFunctions.EQUAL,
            Comparison.NOT_EQUAL: LFunctions.NOT_EQUAL,
            Comparison.LESS: LFunctions.LESS,
            Comparison.LESS_EQUAL: LFunctions.LESS_EQUAL,
            Comparison.GREATER: LFunctions.GREATER,
            Comparison.GREATER_EQUAL: LFunctions.GREATER_EQUAL,
            Comparison.MULTIPLE: LFunctions.MULTIPLE,
            Comparison.POWER: LFunctions.POWER,
        })


class LExpression:
    def __init__(self, name: LFunctions, args: list):
        self.elements = [name, *filter(lambda x: x is not None, args)]

    def __repr__(self):
        return f'[{', '.join(repr(e) for e in self.elements)}]'


class LVisitor(Visitor):
    def block(self, block: Block) -> LExpression:
        return LExpression(LFunctions.from_quantifier(block.quantifier), self.accept_all(block.statements))

    def attribute_statement(self, stmt: AttributeStatement) -> LExpression:
        return LExpression(LFunctions.from_comparison(stmt.comparison), [
            LExpression(LFunctions.ATTR, [stmt.identifier]),
            self.accept(stmt.expression),
        ])

    def with_statement(self, stmt: WithStatement) -> LExpression:
        return LExpression(LFunctions.WITH, [
            stmt.kind,
            self.accept(stmt.predicate),
            self.accept(stmt.block),
        ])

    def predicate(self, predicate: Predicate) -> int | LExpression:
        return predicate.literal if predicate.literal else self.accept(predicate.reference)

    def binary_expression(self, expr: BinaryExpression) -> LExpression:
        op = expr.operator.switch({
            Operator.PLUS: operator.add,
            Operator.MINUS: operator.sub,
            Operator.MULTIPLICATION: operator.mul,
            Operator.DIVISION: operator.truediv,
        })

        return op(self.accept(expr.left), self.accept(expr.right))

    def literal_expression(self, expr: LiteralExpression) -> int | str:
        return expr.literal


def encode_constraint(constraint: MainConstraint) -> LExpression:
    return LVisitor().accept(constraint.block)
