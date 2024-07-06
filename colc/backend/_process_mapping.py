from colc.frontend import ast, Operator

from ._context import Context
from ._instruction import Instruction, Opcode
from ._scope import VisitorWithScope


def process_mappings(ctx: Context) -> dict[str, list[Instruction]]:
    return {it.identifier.name: process_mapping(ctx, it) for it in ctx.file.mappings}


def process_mapping(ctx: Context, mapping: ast.MDefinition) -> list[Instruction]:
    visitor = VisitorImpl(ctx)
    visitor.accept(mapping.block)

    return visitor.instructions


class VisitorImpl(VisitorWithScope):
    def __init__(self, ctx: Context):
        super().__init__()
        self.ctx = ctx
        self.instructions: list[Instruction] = []

    def f_block(self, block: ast.FBlock):
        self.accept_all(block.statements)

    def f_statement_assign(self, stmt: ast.FStatementAssign):
        self.accept(stmt.expression)

        value = self.scope.declare(stmt.identifier)
        self.instructions.append(Opcode.I_STORE.new(value.index))

    def f_statement_block(self, stmt: ast.FStatementBlock):
        self.accept_with_scope(self.scope.new_child_scope(), stmt.block)

    def expression_binary(self, expr: ast.ExpressionBinary):
        self.accept(expr.left)
        self.accept(expr.right)

        # TODO: add type inference
        op = expr.operator.switch(
            {
                Operator.PLUS: 0,
                Operator.MINUS: 1,
                Operator.MULTIPLICATION: 2,
                Operator.DIVISION: 3,
            }
        )
        self.instructions.append(Opcode.I_OP.new(op))

    def expression_literal(self, expr: ast.ExpressionLiteral):
        index = self.ctx.intern_const(expr.literal)
        self.instructions.append(Opcode.I_CONST.new(index))

    def expression_ref(self, expr: ast.ExpressionRef):
        value = self.scope.lookup(expr.identifier)
        self.instructions.append(Opcode.I_LOAD.new(value.index))
