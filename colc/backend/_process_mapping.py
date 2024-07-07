from colc.frontend import ast, Value, Type

from ._context import Context
from ._instruction import Instruction, Opcode
from ._scope import VisitorWithScope
from ._operator import op_evaluate
from ._process_expression import process_expression


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

        self.scope.define_synthetic('root', Value(Type.NODE))

    def accept_expr(self, expr: ast.Expression, load: bool = False) -> Value:
        # this is backtracking search, not very fast but works great
        value = process_expression(self.scope, expr)

        # if value could not be determined at compile time, generate instructions
        if value is None:
            return self.accept(expr)

        # if value was determined at compile time, load value onto stack
        if load:
            index = self.ctx.intern_const(value.comptime)
            self.instructions.append(Opcode.CONST.new(index))

        return value

    def f_block(self, block: ast.FBlock):
        self.accept_all(block.statements)

    def f_statement_assign(self, stmt: ast.FStatementAssign):
        value = self.accept_expr(stmt.expression)
        definition = self.scope.define(stmt.identifier, value)

        if not value.is_comptime:
            self.instructions.append(Opcode.STORE.new(definition.index))

    def f_statement_block(self, stmt: ast.FStatementBlock):
        self.accept_with_scope(self.scope.new_child_scope(), stmt.block)

    def expression_binary(self, expr: ast.ExpressionBinary):
        left = self.accept_expr(expr.left, load=True)
        right = self.accept_expr(expr.right, load=True)

        self.instructions.append(Opcode.from_operator(expr.operator).new(0))

        return op_evaluate(expr.operator, left, right)

    def expression_literal(self, expr: ast.ExpressionLiteral) -> Value:
        return expr.value

    def expression_ref(self, expr: ast.ExpressionRef) -> Value:
        definition = self.scope.lookup(expr.identifier)

        if not definition.is_comptime:
            self.instructions.append(Opcode.LOAD.new(definition.index))

        return definition.value

    def expression_attr(self, expr: ast.ExpressionAttr):
        definition = self.scope.lookup(expr.identifier)
        self.instructions.append(Opcode.LOAD.new(definition.index))

        index = self.ctx.intern_const(expr.attribute.name)
        self.instructions.append(Opcode.CONST.new(index))

        self.instructions.append(Opcode.ATTR.new(0))

        # the type of a node property is not known
        return Value.default()
