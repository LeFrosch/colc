from typing import Collection

from colc.common import fatal_problem, internal_problem
from colc.frontend import ast, ComptimeValue, Quantifier

from ._context import Context
from ._scope import Scope, VisitorWithScope
from ._lexpression import LExpression, LFunction
from ._process_expression import process_expression
from ._config import Optimization


def process_constraint(ctx: Context) -> LExpression:
    constraint = ctx.file.constraint_main()
    return VisitorImpl(ctx).accept(constraint.block)


class VisitorImpl(VisitorWithScope):
    def __init__(self, ctx: Context):
        super().__init__()
        self.ctx = ctx

    def scope_from_call(self, call: ast.Call, target) -> Scope:
        arguments = call.arguments
        parameters = target.parameters

        if len(arguments) < len(parameters):
            fatal_problem('not enough arguments', call.identifier)
        if len(arguments) > len(parameters):
            fatal_problem('too many arguments', call.identifier)

        scope = Scope()
        for param, arg in zip(parameters, arguments):
            value = self.accept_expr(arg)
            scope.define(param, value)

        return scope

    def accept_expr(self, expr: ast.Expression) -> ComptimeValue:
        value = process_expression(self.scope, expr)

        if value is None:
            internal_problem('non comptime value in constraint')

        return value

    def accept_block(self, quantifier: Quantifier, statements: Collection[ast.Node]) -> LExpression:
        expressions = self.accept_all(statements)

        if len(expressions) == 1 and self.ctx.config.enabled(Optimization.REDUNDANT_QUANTIFIER):
            return expressions[0]
        else:
            return LExpression(LFunction.from_quantifier(quantifier), expressions)

    def accept_predicate(self, call: ast.Call) -> LExpression:
        target = self.ctx.file.predicate(call.identifier)
        scope = self.scope_from_call(call, target)

        return self.accept_with_scope(scope, target.block)

    def c_block(self, block: ast.CBlock) -> LExpression:
        return self.accept_block(block.quantifier, block.statements)

    def c_statement_block(self, stmt: ast.CStatementBlock) -> LExpression:
        return self.c_block(stmt.block)

    def c_statement_attr(self, stmt: ast.CStatementAttr) -> LExpression:
        return LExpression(
            LFunction.from_comparison(stmt.comparison),
            [
                LExpression(LFunction.ATTR, [stmt.identifier.name]),
                self.accept_expr(stmt.expression).comptime,
            ],
        )

    def c_statement_with(self, stmt: ast.CStatementWith) -> LExpression:
        return LExpression(
            LFunction.WITH,
            [
                stmt.kind.name,
                self.accept_predicate(stmt.predicate),
                self.accept(stmt.block),
            ],
        )

    def c_statement_call(self, stmt: ast.CStatementCall) -> LExpression:
        constraint = self.ctx.file.constraint_type(stmt.constraint.identifier)
        constraint_scope = self.scope_from_call(stmt.constraint, constraint)

        return LExpression(
            LFunction.WITH,
            [
                constraint.kind.name,
                self.accept_predicate(stmt.predicate),
                self.accept_with_scope(constraint_scope, constraint.block),
            ],
        )

    def p_block(self, block: ast.PBlock) -> LExpression:
        return self.accept_block(block.quantifier, block.statements)

    def p_statement_block(self, stmt: ast.PStatementBlock) -> LExpression:
        return self.p_block(stmt.block)

    def p_statement_size(self, stmt: ast.PStatementSize) -> LExpression:
        return LExpression(
            LFunction.from_comparison(stmt.comparison),
            [
                LExpression(LFunction.LIST_SIZE, []),
                self.accept_expr(stmt.expression).comptime,
            ],
        )

    def p_statement_aggr(self, stmt: ast.PStatementAggr) -> LExpression:
        return LExpression(
            LFunction.from_comparison(stmt.comparison),
            [
                LExpression(LFunction.from_aggregator(stmt.aggregator), [stmt.kind.name]),
                self.accept_expr(stmt.expression).comptime,
            ],
        )
