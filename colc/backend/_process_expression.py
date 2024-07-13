from typing import Optional

from colc.common import internal_problem, ComptimeValue, NoneValue
from colc.frontend import ast

from ._scope import Scope, VisitorWithScope, ComptimeDefinition
from ._context import Context
from ._functions import operator_evaluate
from ._utils import zip_call_arguments, check_assignment


class CannotProcessAtComptime(Exception):
    def __init__(self, what: ast.Node):
        self.what = what


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


class ComptimeVisitorImpl(VisitorWithScope):
    def __init__(self, ctx: Context, scope: Scope):
        super().__init__(scope)
        self.ctx = ctx

    def new_scope_for_call(self, call: ast.Call, target) -> Scope:
        scope = self.scope.new_call_scope()

        for arg, param in zip_call_arguments(call, target):
            value = self.accept(arg)
            scope.insert_comptime(param, value, final=True)

        return scope

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
            raise CannotProcessAtComptime(expr)

    def expression_attr(self, expr: ast.ExpressionAttr) -> ComptimeValue:
        raise CannotProcessAtComptime(expr)

    def expression_call(self, expr: ast.ExpressionCall) -> ComptimeValue:
        func = self.ctx.file.function(expr.call.identifier)
        func_scope = self.new_scope_for_call(expr.call, func)

        try:
            self.accept_with_scope(func_scope, func.block)
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

    def f_statement_define(self, stmt: ast.FStatementDefine):
        value = self.accept(stmt.expression)
        self.scope.insert_comptime(stmt.identifier, value, final=not stmt.qualifier.is_var)

    def f_statement_assign(self, stmt: ast.FStatementAssign):
        value = self.accept(stmt.expression)

        definition = self.scope.lookup(stmt.identifier)
        check_assignment(stmt.identifier, definition, value)
        assert isinstance(definition, ComptimeDefinition)

        definition.value.comptime = value.comptime

    def f_statement_if(self, stmt: ast.FStatementIf):
        value = self.accept(stmt.condition)

        if value.comptime:
            self.accept(stmt.if_block)
        elif stmt.else_block is not None:
            self.accept(stmt.else_block)
