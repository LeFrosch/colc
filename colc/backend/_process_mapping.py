from colc.common import fatal_problem
from colc.frontend import ast, Value, AnyValue, ComptimeValue, Type

from ._context import Context
from ._instruction import Instruction, Opcode
from ._scope import Scope, VisitorWithScope, RuntimeDefinition
from ._process_expression import process_expression
from ._functions import operator_infer
from ._utils import Allocator, JmpAnchor, zip_call_arguments, check_assignment


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
        self.allocator = Allocator()
        self.instructions: list[Instruction] = []

        self.scope.insert_synthetic('root', Type.NODE, self.allocator.alloc())

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
        # this is backtracking search, not very fast but works great
        value = process_expression(self.ctx, self.scope, expr)

        # if value could not be determined at compile time, generate instructions
        if value is None:
            value = self.accept(expr)

        # if value was determined at compile time, load value onto stack
        if load and value.is_comptime:
            self.instruction_for_const(value)

        return value

    def new_scope_for_call(self, call: ast.Call, target) -> Scope:
        scope = self.scope.new_call_scope()

        for arg, param in zip_call_arguments(call, target):
            value = self.accept_expr(arg)

            if isinstance(value, ComptimeValue):
                scope.insert_comptime(param, value, final=True)
            else:
                scope.insert_runtime(param, value, self.allocator.alloc(), final=True)

        return scope

    def f_block(self, block: ast.FBlock):
        self.accept_all(block.statements)

    def f_statement_define(self, stmt: ast.FStatementDefine):
        value = self.accept_expr(stmt.expression, load=not stmt.qualifier.is_const)

        if stmt.qualifier.is_const:
            if not isinstance(value, ComptimeValue):
                fatal_problem('cannot assign runtime value', stmt.identifier)

            self.scope.insert_comptime(stmt.identifier, value, final=True)
        else:
            definition = self.scope.insert_runtime(
                stmt.identifier,
                value,
                self.allocator.alloc(),
                final=stmt.qualifier.is_final,
            )
            self.instructions.append(Opcode.STORE.new(definition.index, definition.name))

    def f_statement_assign(self, stmt: ast.FStatementAssign):
        value = self.accept_expr(stmt.expression, load=True)

        definition = self.scope.lookup(stmt.identifier)
        check_assignment(stmt.identifier, definition, value)

        # it is only possible to assign to runtime definitions, comptime should always be final in this case
        assert isinstance(definition, RuntimeDefinition)

        self.instructions.append(Opcode.STORE.new(definition.index, definition.name))

    def f_statement_block(self, stmt: ast.FStatementBlock):
        self.accept_with_child_scope(stmt.block)

    def f_statement_if(self, stmt: ast.FStatementIf):
        value = self.accept_expr(stmt.condition, load=True)

        if not value.assignable_to(Type.BOOLEAN):
            fatal_problem('expected <bool>', stmt.condition)

        jmp_end = JmpAnchor(self.instructions, Opcode.JMP_FF)
        self.accept_with_child_scope(stmt.if_block)

        if stmt.else_block is not None:
            jmp = JmpAnchor(self.instructions, Opcode.JMP_F)

            jmp_end.set_address()
            jmp_end = jmp

            self.accept_with_child_scope(stmt.else_block)

        jmp_end.set_address()

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
        definition = self.scope.lookup(expr.identifier, expected=Type.NODE)
        assert isinstance(definition, RuntimeDefinition)

        self.instructions.append(Opcode.LOAD.new(definition.index, expr.identifier.name))

        index = self.ctx.intern_const(expr.attribute.name)
        self.instructions.append(Opcode.ATTR.new(index, expr.attribute.name))

        # the type of a node property is not known
        return AnyValue
