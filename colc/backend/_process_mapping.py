from colc.common import fatal_problem, Value, AnyValue, ComptimeValue, types, RuntimeValue, unreachable
from colc.frontend import ast

from ._context import Context
from ._instruction import Instruction, Opcode
from ._scope import VisitorWithScope, RuntimeDefinition
from ._process_expression import process_expression
from ._functions import operator_binary_infer, operator_unary_infer, resolve_function, BuiltinFunction, DefinedFunction
from ._jmp_anchor import JmpAnchor
from ._utils import Allocator, check_arguments, check_assignment, check_compatible
from ._mapping import Mapping


def process_mappings(ctx: Context) -> list[Mapping]:
    mappings = ctx.file.mappings
    if len(mappings) == 0:
        fatal_problem('no mapping')
    if all(len(it.labels) > 0 for it in mappings):
        fatal_problem('no unconditional mapping')

    return [
        Mapping(
            name=mapping.identifier.name,
            labels=[_lookup_label(ctx, it) for it in mapping.labels],
            code=process_mapping(ctx, mapping),
        )
        for mapping in mappings
    ]


def _lookup_label(ctx: Context, identifier: ast.Identifier) -> int:
    label = ctx.lookup_label(identifier.name)
    if label is None:
        fatal_problem('undefined identifier', identifier)

    return label


def process_mapping(ctx: Context, mapping: ast.MDefinition) -> list[Instruction]:
    visitor = VisitorImpl(ctx)
    visitor.accept(mapping.block)
    visitor.finalize()

    return visitor.instructions


class VisitorImpl(VisitorWithScope):
    def __init__(self, ctx: Context):
        super().__init__()
        self.ctx = ctx
        self.allocator = Allocator()
        self.instructions: list[Instruction] = []

        self.scope.insert_synthetic('root', types.NODE, self.allocator.alloc())

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

    def accept_expr(self, expr: ast.Expression, load: bool = True) -> Value:
        # this is backtracking search, not very fast but works great
        value = process_expression(self.ctx, self.scope, expr)

        # if value could not be determined at compile time, generate instructions
        if value is None:
            value = self.accept(expr)

        # if value was determined at compile time, load value onto stack
        if load and value.is_comptime:
            self.instruction_for_const(value)

        return value

    def f_block(self, block: ast.FBlock):
        for stmt in block.statements:
            self.accept(stmt)

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
        value = self.accept_expr(stmt.expression)

        definition = self.scope.lookup(stmt.identifier)
        check_assignment(stmt.identifier, definition, value.type)

        # it is only possible to assign to runtime definitions, comptime should always be final in this case
        assert isinstance(definition, RuntimeDefinition)

        self.instructions.append(Opcode.STORE.new(definition.index, definition.name))

    def f_statement_block(self, stmt: ast.FStatementBlock):
        self.accept_with_child_scope(stmt.block)

    def f_statement_return(self, stmt: ast.FStatementReturn):
        if stmt.expression is not None:
            value = self.accept_expr(stmt.expression)
            self.scope.insert_return(value.type)

        anchor = JmpAnchor(self.instructions, Opcode.JMP_F)
        self.scope.insert_jmp_anchor(anchor)

    def f_statement_if(self, stmt: ast.FStatementIf):
        value = self.accept_expr(stmt.condition)
        check_compatible(stmt.condition, value, types.BOOLEAN)

        jmp_end = JmpAnchor(self.instructions, Opcode.JMP_FF)
        self.accept_with_child_scope(stmt.if_block)

        if stmt.else_block is not None:
            jmp = JmpAnchor(self.instructions, Opcode.JMP_F)

            jmp_end.set_address()
            jmp_end = jmp

            self.accept_with_child_scope(stmt.else_block)

        jmp_end.set_address()

    def f_statement_for(self, stmt: ast.FStatementFor):
        list_value = self.accept_expr(stmt.condition)
        check_compatible(stmt.condition, list_value, types.ANY_LIST)

        # loop header: store list in unnamed local variable
        list_index = self.allocator.alloc()
        self.instructions.append(Opcode.STORE.new(list_index, 'for'))

        # loop start: check if there is a next value
        start = len(self.instructions)
        self.instructions.append(Opcode.HAS_NEXT.new(list_index))
        jmp_end = JmpAnchor(self.instructions, Opcode.JMP_FF)

        # loop body: store current value and run block
        self.instructions.append(Opcode.NEXT.new(list_index))
        var_index = self.allocator.alloc()
        self.instructions.append(Opcode.STORE.new(var_index, stmt.identifier.name))

        scope = self.scope.new_child_scope()
        scope.insert_runtime(stmt.identifier, RuntimeValue(list_value.type.as_scalar), var_index, final=True)

        self.accept_with_scope(scope, stmt.block)

        # loop end: jump back to start
        end = len(self.instructions)
        self.instructions.append(Opcode.JMP_B.new(end - start, str(start)))

        jmp_end.set_address()

    def expression_unary(self, expr: ast.ExpressionUnary) -> Value:
        value = self.accept_expr(expr.expression)
        self.instructions.append(Opcode.from_operator_unary(expr.operator).new(0))
        return operator_unary_infer(expr.operator, value)

    def expression_binary(self, expr: ast.ExpressionBinary) -> Value:
        left = self.accept_expr(expr.left)
        right = self.accept_expr(expr.right)

        self.instructions.append(Opcode.from_operator_binary(expr.operator).new(0))

        return operator_binary_infer(expr.operator, left, right)

    def expression_literal(self, expr: ast.ExpressionLiteral) -> Value:
        return expr.value

    def expression_ref(self, expr: ast.ExpressionRef) -> Value:
        definition = self.scope.lookup(expr.identifier)

        if isinstance(definition, RuntimeDefinition):
            self.instructions.append(Opcode.LOAD.new(definition.index, expr.identifier.name))

        return definition.value

    def expression_attr(self, expr: ast.ExpressionAttr) -> Value:
        definition = self.scope.lookup(expr.identifier, expected=types.NODE)
        assert isinstance(definition, RuntimeDefinition)

        self.instructions.append(Opcode.LOAD.new(definition.index, expr.identifier.name))

        index = self.ctx.intern_const(expr.attribute.name)
        self.instructions.append(Opcode.ATTR.new(index, expr.attribute.name))

        # the type of a node property is not known
        return AnyValue

    def accept_builtin_function(self, call: ast.Call, func: BuiltinFunction) -> Value:
        check_arguments(call, func)

        for arg, param in zip(call.arguments, func.parameters):
            value = self.accept_expr(arg)
            check_compatible(arg, value, param)

        self.instructions.append(func.opcode.new(0))
        return RuntimeValue(func.returns)

    def accept_defined_function(self, call: ast.Call, func: DefinedFunction) -> Value:
        check_arguments(call, func)

        scope = self.scope.new_call_scope()
        for arg, param in zip(call.arguments, func.definition.parameters):
            value = self.accept_expr(arg, load=False)

            if isinstance(value, ComptimeValue):
                scope.insert_comptime(param, value, final=True)
            else:
                definition = scope.insert_runtime(param, value, self.allocator.alloc(), final=True)
                self.instructions.append(Opcode.STORE.new(definition.index, definition.name))

        self.accept_with_scope(scope, func.definition.block)
        return RuntimeValue(scope.returns())

    def expression_call(self, expr: ast.ExpressionCall) -> Value:
        func = resolve_function(self.ctx.file, expr.call.identifier)

        if isinstance(func, BuiltinFunction):
            return self.accept_builtin_function(expr.call, func)

        if isinstance(func, DefinedFunction):
            return self.accept_defined_function(expr.call, func)

        unreachable()
