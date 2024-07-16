from typing import Collection, Any, Optional

from colc.common import internal_problem, ComptimeValue, AnyValue, fatal_problem
from colc.frontend import ast, Quantifier, Comparison

from ._context import Context
from ._scope import Scope, VisitorWithScope
from ._lexpression import LExpression, LFunction
from ._process_expression import process_expression
from ._config import Optimization
from ._functions import comparison_infer


def process_constraint(ctx: Context) -> LExpression:
    constraint = ctx.file.constraint_main()

    visitor = VisitorImpl(ctx)
    result = visitor.accept(constraint.block)
    visitor.finalize()

    return result


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

    def accept_label(self, label: Optional[ast.Label]) -> Optional[int]:
        if label is None:
            return None

        return self.ctx.intern_label(label.identifier.name)

    def new_scope_for_call(self, call: ast.Call, parameters: list[ast.Identifier]) -> Scope:
        if len(call.arguments) != len(parameters):
            fatal_problem(f'expected {len(parameters)} arguments', call)

        scope = self.scope.new_call_scope()

        for arg, param in zip(call.arguments, parameters):
            value = self.accept_expr(arg)
            scope.insert_comptime(param, value, final=True)

        return scope

    def accept_predicate(self, call: ast.Call) -> LExpression:
        target = self.ctx.file.predicate(call.identifier)
        target_scope = self.new_scope_for_call(call, target.parameters)

        return self.accept_with_scope(target_scope, target.block)

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
                self.accept_label(stmt.label),
                stmt.kind.name,
                self.accept_predicate(stmt.predicate),
                self.accept(stmt.block),
            ],
        )

    def c_statement_call(self, stmt: ast.CStatementCall) -> LExpression:
        constraint = self.ctx.file.constraint_type(stmt.constraint.identifier)
        constraint_scope = self.new_scope_for_call(stmt.constraint, constraint.parameters)

        return LExpression(
            LFunction.WITH,
            [
                self.accept_label(stmt.label),
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
