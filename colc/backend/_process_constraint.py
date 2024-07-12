from typing import Collection, Any

from colc.common import internal_problem
from colc.frontend import ast, ComptimeValue, Quantifier, Comparison, AnyValue

from ._context import Context
from ._scope import VisitorWithScope
from ._lexpression import LExpression, LFunction
from ._process_expression import process_expression, scope_from_call
from ._config import Optimization
from ._functions import comparison_infer


def process_constraint(ctx: Context) -> LExpression:
    constraint = ctx.file.constraint_main()
    return VisitorImpl(ctx).accept(constraint.block)


class VisitorImpl(VisitorWithScope):
    def __init__(self, ctx: Context):
        super().__init__()
        self.ctx = ctx

    def accept_expr(self, expr: ast.Expression) -> ComptimeValue:
        value = process_expression(self.ctx, self.scope, expr)

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
        scope = scope_from_call(self.scope, call, target, self.accept_expr)

        return self.accept_with_scope(scope, target.block)

    def accept_comparison(self, comparison: Comparison, expr: ast.Expression) -> Any:
        value = self.accept_expr(expr)
        comparison_infer(comparison, AnyValue, value)

        return value.comptime

    def c_block(self, block: ast.CBlock) -> LExpression:
        return self.accept_block(block.quantifier, block.statements)

    def c_statement_block(self, stmt: ast.CStatementBlock) -> LExpression:
        return self.c_block(stmt.block)

    def c_statement_attr(self, stmt: ast.CStatementAttr) -> LExpression:
        return LExpression(
            LFunction.from_comparison(stmt.comparison),
            [
                LExpression(LFunction.ATTR, [stmt.identifier.name]),
                self.accept_comparison(stmt.comparison, stmt.expression),
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
        constraint_scope = scope_from_call(self.scope, stmt.constraint, constraint, self.accept_expr)

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
                self.accept_comparison(stmt.comparison, stmt.expression),
            ],
        )

    def p_statement_aggr(self, stmt: ast.PStatementAggr) -> LExpression:
        return LExpression(
            LFunction.from_comparison(stmt.comparison),
            [
                LExpression(LFunction.from_aggregator(stmt.aggregator), [stmt.kind.name]),
                self.accept_comparison(stmt.comparison, stmt.expression),
            ],
        )
