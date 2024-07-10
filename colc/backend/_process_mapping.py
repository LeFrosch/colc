from colc.frontend import ast, Value, DefaultValue, RuntimeValue, ComptimeValue, Type

from ._context import Context
from ._instruction import Instruction, Opcode
from ._scope import VisitorWithScope, RuntimeDefinition
from ._process_expression import process_expression
from ._config import Optimization
from ._functions import operator_infer


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

        self.scope.define_synthetic('root', RuntimeValue({Type.NODE}))

    def instruction_for_const(self, value: ComptimeValue):
        comptime = value.comptime

        if comptime is True:
            instruction = Opcode.TRUE.new(0)
        elif comptime is False:
            instruction = Opcode.FALSE.new(0)
        elif isinstance(comptime, int) and 0 <= comptime <= 255:
            instruction = Opcode.INT.new(comptime)
        else:
            index = self.ctx.intern_const(comptime)
            instruction = Opcode.CONST.new(index, repr(comptime))

        self.instructions.append(instruction)

    def accept_expr(self, expr: ast.Expression, load: bool = False) -> Value:
        if self.ctx.config.enabled(Optimization.COMPTIME_EVALUATION):
            # this is backtracking search, not very fast but works great
            value = process_expression(self.ctx, self.scope, expr)
        else:
            value = None

        # if value could not be determined at compile time, generate instructions
        if value is None:
            value = self.accept(expr)

        # if value was determined at compile time, load value onto stack
        if load and value.is_comptime:
            self.instruction_for_const(value)

        return value

    def f_block(self, block: ast.FBlock):
        self.accept_all(block.statements)

    def f_statement_assign(self, stmt: ast.FStatementAssign):
        value = self.accept_expr(stmt.expression)
        definition = self.scope.define(stmt.identifier, value)

        if isinstance(definition, RuntimeDefinition):
            self.instructions.append(Opcode.STORE.new(definition.index, definition.name))

    def f_statement_block(self, stmt: ast.FStatementBlock):
        self.accept_with_scope(self.scope.new_child_scope(), stmt.block)

    def expression_binary(self, expr: ast.ExpressionBinary) -> Value:
        left = self.accept_expr(expr.left, load=True)
        right = self.accept_expr(expr.right, load=True)

        self.instructions.append(Opcode.from_operator(expr.operator).new(0))

        return operator_infer(expr.operator, left, right)

    def expression_literal(self, expr: ast.ExpressionLiteral) -> Value:
        return expr.value

    def expression_ref(self, expr: ast.ExpressionRef) -> Value:
        definition = self.scope.lookup(expr.identifier)

        if isinstance(definition, RuntimeDefinition):
            self.instructions.append(Opcode.LOAD.new(definition.index, expr.identifier.name))

        return definition.value

    def expression_attr(self, expr: ast.ExpressionAttr):
        definition = self.scope.lookup_runtime(expr.identifier, expected=Type.NODE)
        self.instructions.append(Opcode.LOAD.new(definition.index, expr.identifier.name))

        index = self.ctx.intern_const(expr.attribute.name)
        self.instructions.append(Opcode.ATTR.new(index, expr.attribute.name))

        # the type of a node property is not known
        return DefaultValue
