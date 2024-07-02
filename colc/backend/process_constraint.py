import operator

from colc.frontend import *

from .scope import Scope
from .file import File
from .lexpression import LExpression, LFunction


def process_constraint(file: File) -> LExpression:
    constraint = file.constraint_main()
    return ConstraintVisitor(file, Scope()).accept(constraint.block)


class ConstraintVisitor(Visitor):
    def __init__(self, file: File, scope: Scope):
        self.file = file
        self.scope = scope

    def c_block(self, block: CBlock) -> LExpression:
        return LExpression(LFunction.from_quantifier(block.quantifier), self.accept_all(block.statements))

    def c_statement_block(self, stmt: CStatementBlock) -> LExpression:
        return self.c_block(stmt.block)

    def c_statement_attr(self, stmt: CStatementAttr) -> LExpression:
        return LExpression(
            LFunction.from_comparison(stmt.comparison),
            [
                LExpression(LFunction.ATTR, [stmt.identifier.name]),
                self.accept(stmt.expression),
            ],
        )

    def _predicate(self, call: Call) -> LExpression:
        arguments = self.accept_all(call.arguments)

        target = self.file.predicate(call.identifier)
        target_scope = Scope.from_call(call, target.parameters, arguments)

        return ConstraintVisitor(self.file, target_scope).accept(target.block)

    def c_statement_with(self, stmt: CStatementWith) -> LExpression:
        return LExpression(
            LFunction.WITH,
            [
                stmt.kind.name,
                self._predicate(stmt.predicate),
                self.accept(stmt.block),
            ],
        )

    def c_statement_call(self, stmt: CStatementCall) -> LExpression:
        arguments = self.accept_all(stmt.constraint.arguments)

        target = self.file.constraint_type(stmt.constraint.identifier)
        target_scope = Scope.from_call(stmt.constraint, target.parameters, arguments)
        target_visitor = ConstraintVisitor(self.file, target_scope)

        return LExpression(
            LFunction.WITH,
            [
                target.kind.name,
                self._predicate(stmt.predicate),
                target_visitor.accept(target.block),
            ],
        )

    def p_block(self, block: PBlock) -> LExpression:
        return LExpression(LFunction.from_quantifier(block.quantifier), self.accept_all(block.statements))

    def p_statement_block(self, stmt: PStatementBlock) -> LExpression:
        return self.p_block(stmt.block)

    def p_statement_size(self, stmt: PStatementSize) -> LExpression:
        return LExpression(
            LFunction.from_comparison(stmt.comparison),
            [LExpression(LFunction.LIST_SIZE, []), self.accept(stmt.expression)],
        )

    def p_statement_aggr(self, stmt: PStatementAggr) -> LExpression:
        return LExpression(
            LFunction.from_comparison(stmt.comparison),
            [
                LExpression(LFunction.from_aggregator(stmt.aggregator), [stmt.kind.name]),
                self.accept(stmt.expression),
            ],
        )

    def expression_binary(self, expr: ExpressionBinary) -> LExpression:
        op = expr.operator.switch(
            {
                Operator.PLUS: operator.add,
                Operator.MINUS: operator.sub,
                Operator.MULTIPLICATION: operator.mul,
                Operator.DIVISION: operator.truediv,
            }
        )

        return op(self.accept(expr.left), self.accept(expr.right))

    def expression_literal(self, expr: ExpressionLiteral) -> int | str:
        return expr.literal

    def expression_ref(self, expr: ExpressionRef) -> int | str:
        return self.scope.lookup(expr.identifier)
