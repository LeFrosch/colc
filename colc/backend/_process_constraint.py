import operator

from colc.frontend import Operator, ast

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
        arguments = self.accept_all(call.arguments)

        target = self.file.predicate(call.identifier)
        target_scope = Scope.from_call(call, target.parameters, arguments)

        return self.accept_with_scope(target_scope, target.block)

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
        arguments = self.accept_all(stmt.constraint.arguments)

        target = self.file.constraint_type(stmt.constraint.identifier)
        target_scope = Scope.from_call(stmt.constraint, target.parameters, arguments)

        return LExpression(
            LFunction.WITH,
            [
                target.kind.name,
                self._predicate(stmt.predicate),
                self.accept_with_scope(target_scope, target.block),
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

    def expression_binary(self, expr: ast.ExpressionBinary) -> LExpression:
        op = expr.operator.switch(
            {
                Operator.PLUS: operator.add,
                Operator.MINUS: operator.sub,
                Operator.MULTIPLICATION: operator.mul,
                Operator.DIVISION: operator.truediv,
            }
        )

        return op(self.accept(expr.left), self.accept(expr.right))

    def expression_literal(self, expr: ast.ExpressionLiteral) -> int | str:
        return expr.literal

    def expression_ref(self, expr: ast.ExpressionRef) -> int | str:
        return self.scope.lookup(expr.identifier).data
