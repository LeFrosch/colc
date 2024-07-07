from colc.common import fatal_problem
from colc.frontend import ast

from ._context import Context
from ._file import File
from ._scope import Scope, VisitorWithScope
from ._lexpression import LExpression, LFunction


def process_constraint(ctx: Context) -> LExpression:
    constraint = ctx.file.constraint_main()
    return VisitorImpl(ctx.file).accept(constraint.block)


class VisitorImpl(VisitorWithScope):
    def __init__(self, file: File):
        super().__init__()
        self.file = file

    def scope_from_call(self, call: ast.Call, target) -> Scope:
        arguments = call.arguments
        parameters = target.parameters

        if len(arguments) < len(parameters):
            fatal_problem('not enough arguments', call.identifier)
        if len(arguments) > len(parameters):
            fatal_problem('too many arguments', call.identifier)

        scope = Scope()
        for param, arg in zip(parameters, arguments):
            value = self.accept(arg)
            scope.define(param, value)

        return scope

    def c_block(self, block: ast.CBlock) -> LExpression:
        return LExpression(LFunction.from_quantifier(block.quantifier), self.accept_all(block.statements))

    def c_statement_block(self, stmt: ast.CStatementBlock) -> LExpression:
        return self.c_block(stmt.block)

    def c_statement_attr(self, stmt: ast.CStatementAttr) -> LExpression:
        return LExpression(
            LFunction.from_comparison(stmt.comparison),
            [
                LExpression(LFunction.ATTR, [stmt.identifier.name]),
                self.accept(stmt.expression),
            ],
        )

    def _predicate(self, call: ast.Call) -> LExpression:
        target = self.file.predicate(call.identifier)
        scope = self.scope_from_call(call, target)

        return self.accept_with_scope(scope, target.block)

    def c_statement_with(self, stmt: ast.CStatementWith) -> LExpression:
        return LExpression(
            LFunction.WITH,
            [
                stmt.kind.name,
                self._predicate(stmt.predicate),
                self.accept(stmt.block),
            ],
        )

    def c_statement_call(self, stmt: ast.CStatementCall) -> LExpression:
        constraint = self.file.constraint_type(stmt.constraint.identifier)
        constraint_scope = self.scope_from_call(stmt.constraint, constraint)

        return LExpression(
            LFunction.WITH,
            [
                constraint.kind.name,
                self._predicate(stmt.predicate),
                self.accept_with_scope(constraint_scope, constraint.block),
            ],
        )

    def p_block(self, block: ast.PBlock) -> LExpression:
        return LExpression(LFunction.from_quantifier(block.quantifier), self.accept_all(block.statements))

    def p_statement_block(self, stmt: ast.PStatementBlock) -> LExpression:
        return self.p_block(stmt.block)

    def p_statement_size(self, stmt: ast.PStatementSize) -> LExpression:
        return LExpression(
            LFunction.from_comparison(stmt.comparison),
            [LExpression(LFunction.LIST_SIZE, []), self.accept(stmt.expression)],
        )

    def p_statement_aggr(self, stmt: ast.PStatementAggr) -> LExpression:
        return LExpression(
            LFunction.from_comparison(stmt.comparison),
            [
                LExpression(LFunction.from_aggregator(stmt.aggregator), [stmt.kind.name]),
                self.accept(stmt.expression),
            ],
        )

    def expression_binary(self, expr: ast.ExpressionBinary) -> int | str:
        left = self.accept(expr.left)
        right = self.accept(expr.right)

        return expr.operator.evaluate(left, right)

    def expression_literal(self, expr: ast.ExpressionLiteral) -> int | str:
        return expr.literal

    def expression_ref(self, expr: ast.ExpressionRef) -> int | str:
        value = self.scope.lookup(expr.identifier).value
        assert value is not None

        return value
