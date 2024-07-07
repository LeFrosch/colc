from colc.frontend import ast

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

        self.scope.define_synthetic('root')

    def f_block(self, block: ast.FBlock):
        self.accept_all(block.statements)

    def f_statement_assign(self, stmt: ast.FStatementAssign):
        type = self.accept(stmt.expression)

        value = self.scope.define(stmt.identifier, type)
        self.instructions.append(Opcode.STORE.new(value.index))

    def f_statement_block(self, stmt: ast.FStatementBlock):
        self.accept_with_scope(self.scope.new_child_scope(), stmt.block)

    def expression_binary(self, expr: ast.ExpressionBinary):
        self.accept(expr.left)
        self.accept(expr.right)

        self.instructions.append(Opcode.from_operator(expr.operator).new(0))

    def expression_literal(self, expr: ast.ExpressionLiteral):
        index = self.ctx.intern_const(expr.literal)
        self.instructions.append(Opcode.CONST.new(index))

    def expression_ref(self, expr: ast.ExpressionRef):
        value = self.scope.lookup(expr.identifier)
        self.instructions.append(Opcode.LOAD.new(value.index))
