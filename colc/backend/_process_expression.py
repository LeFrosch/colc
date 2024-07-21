from typing import Optional

from colc.common import internal_problem, ComptimeValue, NoneValue, unreachable, HasLocation, types, fatal_problem, Type
from colc.frontend import ast

from ._scope import Scope, VisitorWithScope, ComptimeDefinition
from ._context import Context
from ._utils import check_arguments, check_assignment, check_compatible
from ._functions import (
    operator_binary_evaluate,
    operator_unary_evaluate,
    resolve_function,
    BuiltinFunction,
    DefinedFunction,
)


class CannotProcessAtComptime(Exception):
    def __init__(self, what: HasLocation):
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

    def expression_unary(self, expr: ast.ExpressionUnary) -> ComptimeValue:
        value = self.accept(expr.expression)
        return operator_unary_evaluate(expr.operator, value)

    def expression_binary(self, expr: ast.ExpressionBinary) -> ComptimeValue:
        left = self.accept(expr.left)
        right = self.accept(expr.right)

        return operator_binary_evaluate(expr.operator, left, right)

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

    def accept_builtin_function(self, call: ast.Call, func: BuiltinFunction) -> ComptimeValue:
        check_arguments(call, func)

        args = []
        for arg, param in zip(call.arguments, func.parameters):
            value = self.accept(arg)
            check_compatible(arg, value, param)

            args.append(value.data)

        result = func.comptime(*args)
        if result is None:
            raise CannotProcessAtComptime(call.identifier)

        return result

    def accept_defined_function(self, call: ast.Call, func: DefinedFunction) -> ComptimeValue:
        check_arguments(call, func)

        _, scope = self.scope.new_call_scope(call.identifier.name)
        for arg, param in zip(call.arguments, func.definition.parameters):
            value = self.accept(arg)

            scope.insert_comptime(param, value, final=True)

        try:
            self.accept_with_scope(scope, func.definition.block)
            return NoneValue
        except ReturnAtComptime as e:
            return e.value

    def expression_call(self, expr: ast.ExpressionCall) -> ComptimeValue:
        func = resolve_function(self.ctx.file, expr.call.identifier)

        if isinstance(func, BuiltinFunction):
            return self.accept_builtin_function(expr.call, func)

        if isinstance(func, DefinedFunction):
            return self.accept_defined_function(expr.call, func)

        unreachable()

    def expression_list(self, expr: ast.ExpressionList) -> ComptimeValue:
        elements = self.accept_all(expr.elements)

        if len(elements) == 0:
            return ComptimeValue([], types.ANY_LIST)

        return ComptimeValue(
            data=[it.data for it in elements],
            type=Type.lup(it.type for it in elements).as_list,
        )

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

        definition.value.data = value.data

    def f_statement_if(self, stmt: ast.FStatementIf):
        value = self.accept(stmt.condition)

        if value.data:
            self.accept(stmt.if_block)
        elif stmt.else_block is not None:
            self.accept(stmt.else_block)

    def f_statement_for(self, stmt: ast.FStatementFor):
        raise CannotProcessAtComptime(stmt)

    def f_statement_fail(self, stmt: ast.FStatementFail):
        value = self.accept(stmt.expression)
        check_compatible(stmt.expression, value, types.STRING)

        fatal_problem('failure: ' + value.data, stmt)

    def f_statement_expr(self, stmt: ast.FStatementExpr):
        self.accept(stmt.expression)
