from colc.common import fatal_problem, Value, AnyValue, ComptimeValue, types, RuntimeValue, unreachable
from colc.frontend import ast

from ._context import Context
from ._instruction import Label, Instruction, InstructionBuffer
from ._opcode import Opcode
from ._scope import VisitorWithScope, RuntimeDefinition
from ._process_expression import process_expression
from ._functions import operator_binary_infer, operator_unary_infer, resolve_function, BuiltinFunction, DefinedFunction
from ._utils import Allocator, check_arguments, check_assignment, check_compatible
from ._mapping import Mapping
from ._fixpoint import fixpoint_can_convert, fixpoint_from_float
from ._process_instructions import process_instructions


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
            code=process_instructions(process_mapping(ctx, mapping)),
        )
        for mapping in mappings
    ]


def _lookup_label(ctx: Context, identifier: ast.Identifier) -> int:
    label = ctx.lookup_label(identifier.name)
    if label is None:
        fatal_problem('undefined identifier', identifier)

    return label


def process_mapping(ctx: Context, mapping: ast.MDefinition) -> InstructionBuffer:
    visitor = VisitorImpl(ctx)
    visitor.accept(mapping.block)
    visitor.finalize()

    return visitor.buffer


class VisitorImpl(VisitorWithScope):
    def __init__(self, ctx: Context):
        super().__init__()
        self.ctx = ctx
        self.allocator = Allocator()
        self.buffer = InstructionBuffer()

        self.scope.insert_synthetic('root', types.NODE, self.allocator.alloc())

    def finalize(self):
        label, _ = self.scope.returns()
        self.buffer.add_label(label)

    def instruction_for_const(self, value: ComptimeValue):
        comptime = value.comptime

        if comptime is True:
            instruction = Instruction(Opcode.TRUE)
        elif comptime is False:
            instruction = Instruction(Opcode.FALSE)
        elif comptime is None:
            instruction = Instruction(Opcode.NONE)
        elif isinstance(comptime, int) and 0 <= comptime <= 255:
            instruction = Instruction(Opcode.INT, argument=comptime)
        elif isinstance(comptime, float) and fixpoint_can_convert(comptime):
            instruction = Instruction(Opcode.FLOAT, argument=fixpoint_from_float(comptime))
        else:
            index = self.ctx.intern_const(comptime)
            instruction = Instruction(Opcode.CONST, argument=index)

        self.buffer.add(instruction)

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
            self.buffer.add(Instruction.new_store(definition.index))

    def f_statement_assign(self, stmt: ast.FStatementAssign):
        value = self.accept_expr(stmt.expression)

        definition = self.scope.lookup(stmt.identifier)
        check_assignment(stmt.identifier, definition, value.type)

        # it is only possible to assign to runtime definitions, comptime should always be final in this case
        assert isinstance(definition, RuntimeDefinition)

        self.buffer.add(Instruction.new_store(definition.index))

    def f_statement_block(self, stmt: ast.FStatementBlock):
        self.accept_with_child_scope(stmt.block)

    def f_statement_return(self, stmt: ast.FStatementReturn):
        if stmt.expression is not None:
            value = self.accept_expr(stmt.expression)
            label = self.scope.insert_return(value.type)
        else:
            self.buffer.add(Instruction(Opcode.NONE))
            label = self.scope.insert_return(types.NONE)

        self.buffer.add(Instruction.new_jmp(Opcode.JMP_F, label))

    def f_statement_if(self, stmt: ast.FStatementIf):
        # evaluate condition
        value = self.accept_expr(stmt.condition)
        check_compatible(stmt.condition, value, types.BOOLEAN)

        # create label for false branch and jmp if false
        label = Label('if_false')
        self.buffer.add(Instruction.new_jmp(Opcode.JMP_FF, label))

        self.accept_with_child_scope(stmt.if_block)

        if stmt.else_block is not None:
            # create unconditional jump to end after true branch
            label_end = Label('if_end')
            self.buffer.add(Instruction.new_jmp(Opcode.JMP_F, label_end))

            # insert label for false branch and
            self.buffer.add_label(label)
            label = label_end

            self.accept_with_child_scope(stmt.else_block)

        self.buffer.add_label(label)

    def f_statement_for(self, stmt: ast.FStatementFor):
        list_value = self.accept_expr(stmt.condition)
        check_compatible(stmt.condition, list_value, types.ANY_LIST)

        # loop header: store list in unnamed local variable
        list_index = self.allocator.alloc()
        self.buffer.add(Instruction.new_store(list_index))

        label_start = Label('for_start')
        label_end = Label('for_end')

        # loop start: check if there is a next value
        self.buffer.add_label(label_start)
        self.buffer.add(Instruction(Opcode.HAS_NEXT, list_index))
        self.buffer.add(Instruction.new_jmp(Opcode.JMP_FF, label_end))

        # loop body: store current value and run block
        self.buffer.add(Instruction(Opcode.NEXT, list_index))
        var_index = self.allocator.alloc()
        self.buffer.add(Instruction.new_store(var_index))

        scope = self.scope.new_child_scope()
        scope.insert_runtime(stmt.identifier, RuntimeValue(list_value.type.as_scalar), var_index, final=True)

        self.accept_with_scope(scope, stmt.block)

        # loop end: jump back to start
        self.buffer.add(Instruction.new_jmp(Opcode.JMP_B, label_start))
        self.buffer.add_label(label_end)

    def expression_unary(self, expr: ast.ExpressionUnary) -> Value:
        value = self.accept_expr(expr.expression)
        self.buffer.add(Instruction.new_unary_operator(expr.operator))
        return operator_unary_infer(expr.operator, value)

    def expression_binary(self, expr: ast.ExpressionBinary) -> Value:
        left = self.accept_expr(expr.left)
        right = self.accept_expr(expr.right)

        self.buffer.add(Instruction.new_binary_operator(expr.operator))

        return operator_binary_infer(expr.operator, left, right)

    def expression_literal(self, expr: ast.ExpressionLiteral) -> Value:
        return expr.value

    def expression_ref(self, expr: ast.ExpressionRef) -> Value:
        definition = self.scope.lookup(expr.identifier)

        if isinstance(definition, RuntimeDefinition):
            self.buffer.add(Instruction.new_load(definition.index))

        return definition.value

    def expression_attr(self, expr: ast.ExpressionAttr) -> Value:
        definition = self.scope.lookup(expr.identifier, expected=types.NODE)
        assert isinstance(definition, RuntimeDefinition)

        self.buffer.add(Instruction.new_load(definition.index))

        index = self.ctx.intern_const(expr.attribute.name)
        self.buffer.add(Instruction(Opcode.ATTR, index))

        # the type of a node property is not known
        return AnyValue

    def accept_builtin_function(self, call: ast.Call, func: BuiltinFunction) -> Value:
        check_arguments(call, func)

        for arg, param in zip(call.arguments, func.parameters):
            value = self.accept_expr(arg)
            check_compatible(arg, value, param)

        self.buffer.add(Instruction(func.opcode))
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
                self.buffer.add(Instruction.new_store(definition.index))

        self.accept_with_scope(scope, func.definition.block)

        label, type = scope.returns()
        self.buffer.add_label(label)

        return RuntimeValue(type)

    def expression_call(self, expr: ast.ExpressionCall) -> Value:
        func = resolve_function(self.ctx.file, expr.call.identifier)

        if isinstance(func, BuiltinFunction):
            return self.accept_builtin_function(expr.call, func)

        if isinstance(func, DefinedFunction):
            return self.accept_defined_function(expr.call, func)

        unreachable()
