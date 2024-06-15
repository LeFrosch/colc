import operator

from frontend.parser import parse
from frontend.ast import *


class LExpression:
    def __init__(self, name: str, args: list):
        self.elements = [name, *filter(lambda x: x is not None, args)]

    def __repr__(self):
        return f'[{', '.join(repr(e) for e in self.elements)}]'


class LVisitor(Visitor):
    def block(self, block: Block) -> LExpression:
        return LExpression(block.quantifier.name, self.accept_all(block.statements))

    def attribute_statement(self, stmt: AttributeStatement) -> LExpression:
        return LExpression(stmt.comparison.name, [
            LExpression('attr', [stmt.identifier]),
            self.accept(stmt.expression),
        ])

    def with_statement(self, stmt: WithStatement) -> LExpression:
        return LExpression('with', [
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


example = '''
con main { all:
  size == 1024 * 5;
  
  2 SOCKET { all:
    5 CORE;
  };
} 
'''

if __name__ == '__main__':
    file = parse(example)
    main = file.main_constraint()

    result = LVisitor().accept(main.block)

    print(result)
