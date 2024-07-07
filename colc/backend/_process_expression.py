from typing import Optional

from colc.frontend import ast, Visitor, ComptimeValue

from ._scope import Scope
from ._operator import op_comptime_evaluate


def process_expression(scope: Scope, expr: ast.Expression) -> Optional[ComptimeValue]:
    return ComptimeVisitorImpl(scope).accept(expr)


class ComptimeVisitorImpl(Visitor):
    def __init__(self, scope: Scope):
        self.scope = scope

    def expression_binary(self, expr: ast.ExpressionBinary) -> Optional[ComptimeValue]:
        left = self.accept(expr.left)
        right = self.accept(expr.right)

        if left is None or right is None:
            return None

        return op_comptime_evaluate(expr.operator, left, right)

    def expression_literal(self, expr: ast.ExpressionLiteral) -> Optional[ComptimeValue]:
        return expr.value

    def expression_ref(self, expr: ast.ExpressionRef) -> Optional[ComptimeValue]:
        value = self.scope.lookup(expr.identifier).value

        if isinstance(value, ComptimeValue):
            return value
        else:
            return None

    def expression_attr(self, expr: ast.ExpressionAttr) -> Optional[ComptimeValue]:
        return None
