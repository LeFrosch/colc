from typing import Optional

from colc.common import fatal_problem, internal_problem
from colc.frontend import ast, ComptimeValue, NoneValue

from ._scope import Scope, VisitorWithScope
from ._context import Context
from ._functions import operator_evaluate


class CannotProcessAtComptime(Exception):
    pass


class ReturnAtComptime(Exception):
    def __init__(self, value: ComptimeValue):
        self.value = value


def process_expression(ctx: Context, scope: Scope, expr: ast.Expression) -> Optional[ComptimeValue]:
    try:
        return ComptimeVisitorImpl(ctx, scope).accept(expr)
    except CannotProcessAtComptime:
        return None
    except ReturnAtComptime:
        internal_problem('leaked return exception')


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
        scope.define(param, value, final=True)

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

        try:
            self.accept_with_scope(scope_from_call(call, func, self.accept), func.block)
            return NoneValue
        except ReturnAtComptime as e:
            return e.value

    def f_block(self, expr: ast.FBlock):
        for stmt in expr.statements:
            self.accept(stmt)

    def f_statement_return(self, stmt: ast.FStatementReturn):
        if stmt.expression is None:
            raise ReturnAtComptime(NoneValue)
        else:
            raise ReturnAtComptime(self.accept(stmt.expression))

    def f_statement_assign(self, stmt: ast.FStatementAssign):
        value = self.accept(stmt.expression)  # this might temporarily change the current scope
        self.scope.define(stmt.identifier, value)

    def f_statement_if(self, stmt: ast.FStatementIf):
        value = self.accept(stmt.condition)

        if value.comptime:
            self.accept(stmt.if_block)
        elif stmt.else_block is not None:
            self.accept(stmt.else_block)
