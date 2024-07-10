from typing import Optional

from colc.common import fatal_problem
from colc.frontend import ast, ComptimeValue

from ._scope import Scope, VisitorWithScope
from ._context import Context
from ._functions import operator_evaluate


class CannotProcessAtComptime(Exception):
    pass


def process_expression(ctx: Context, scope: Scope, expr: ast.Expression) -> Optional[ComptimeValue]:
    try:
        return ComptimeVisitorImpl(ctx, scope).accept(expr)
    except CannotProcessAtComptime:
        return None


def scope_from_call(call: ast.Call, target, accept_expr) -> Scope:
    arguments = call.arguments
    parameters = target.parameters

    if len(arguments) < len(parameters):
        fatal_problem('not enough arguments', call.identifier)
    if len(arguments) > len(parameters):
        fatal_problem('too many arguments', call.identifier)

    scope = Scope()
    for param, arg in zip(parameters, arguments):
        value = accept_expr(arg)
        scope.define(param, value)

    return scope


class ComptimeVisitorImpl(VisitorWithScope):
    def __init__(self, ctx: Context, scope: Scope):
        super().__init__(scope)
        self.ctx = ctx

    def expression_binary(self, expr: ast.ExpressionBinary) -> ComptimeValue:
        left = self.accept(expr.left)
        right = self.accept(expr.right)

        return operator_evaluate(expr.operator, left, right)

    def expression_literal(self, expr: ast.ExpressionLiteral) -> ComptimeValue:
        return expr.value

    def expression_ref(self, expr: ast.ExpressionRef) -> ComptimeValue:
        value = self.scope.lookup(expr.identifier).value

        if isinstance(value, ComptimeValue):
            return value
        else:
            raise CannotProcessAtComptime()

    def expression_attr(self, _: ast.ExpressionAttr) -> ComptimeValue:
        raise CannotProcessAtComptime()

    def expression_call(self, expr: ast.ExpressionCall) -> ComptimeValue:
        call = expr.call
        func = self.ctx.file.function(call.identifier)

        value = self.accept_with_scope(scope_from_call(call, func, self.accept), func.block)
        if value is None:
            fatal_problem('none in expression', call)

        return value

    def f_block(self, expr: ast.FBlock) -> Optional[ComptimeValue]:
        for stmt in expr.statements:
            if isinstance(stmt, ast.FStatementReturn):
                return self.accept(stmt)

            self.accept(stmt)

        return None

    def f_statement_return(self, stmt: ast.FStatementReturn) -> Optional[ComptimeValue]:
        if stmt.expression is None:
            return None
        else:
            return self.accept(stmt.expression)

    def f_statement_assign(self, stmt: ast.FStatementAssign):
        self.scope.define(stmt.identifier, self.accept(stmt.expression))
