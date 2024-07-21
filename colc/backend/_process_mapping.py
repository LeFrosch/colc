from colc.common import (
    fatal_problem,
    Value,
    AnyValue,
    ComptimeValue,
    types,
    RuntimeValue,
    unreachable,
    Type,
    NodeKind,
    comptime_data,
    comptime_list,
)
from colc.frontend import ast

from ._context import Context
from ._instruction import Label, Instruction, InstructionBuffer
from ._opcode import Opcode
from ._scope import VisitorWithScope, RuntimeDefinition, scopes
from ._process_expression import process_expression
from ._functions import operator_binary_infer, operator_unary_infer, resolve_function, BuiltinFunction, DefinedFunction
from ._utils import Allocator, check_arguments, check_assignment, check_compatible
from ._mapping import Mapping
from ._fixpoint import fixpoint_can_convert, fixpoint_from_float


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


def process_mapping(ctx: Context, mapping: ast.MDefinition) -> bytes:
    visitor = VisitorImpl(ctx)
    visitor.accept(mapping.block)
    visitor.finalize()

    return visitor.buffer.build()


class VisitorImpl(VisitorWithScope):
    def __init__(self, ctx: Context):
        super().__init__()
        self.ctx = ctx
        self.allocator = Allocator()
        self.buffer = InstructionBuffer()

        self.scope.insert_synthetic('root', types.NODE, self.allocator.alloc())

    def finalize(self):
        sctx = self.scope.find(scopes.Root)
        assert sctx is not None

        self.buffer.add_label(sctx.end)

    def instruction_for_data(self, value: comptime_data):
        if value is True:
            instruction = Instruction(Opcode.TRUE)
        elif value is False:
            instruction = Instruction(Opcode.FALSE)
        elif value is None:
            instruction = Instruction(Opcode.NONE)
        elif isinstance(value, int) and 0 <= value <= 255:
            instruction = Instruction(Opcode.INT, argument=value)
        elif isinstance(value, float) and fixpoint_can_convert(value):
            instruction = Instruction(Opcode.FLOAT, argument=fixpoint_from_float(value))
        else:
            index = self.ctx.intern_const(value)

            if isinstance(value, NodeKind):
                instruction = Instruction(Opcode.KIND, argument=index)
            else:
                instruction = Instruction(Opcode.CONST, argument=index)

        self.buffer.add(instruction)

    def instruction_for_list(self, value: comptime_list):
        self.buffer.add(Instruction(Opcode.LIST))

        for element in value:
            self.instruction_for_data(element)
            self.buffer.add(Instruction(Opcode.APPEND))

    def instruction_for_const(self, value: ComptimeValue):
        if isinstance(value.data, list):
            self.instruction_for_list(value.data)
        else:
            self.instruction_for_data(value.data)

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

    def f_block(self, block: ast.FBlock) -> bool:
        return any(self.accept_all(block.statements))

    def f_statement_define(self, stmt: ast.FStatementDefine) -> bool:
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

        return False

    def f_statement_assign(self, stmt: ast.FStatementAssign) -> bool:
        value = self.accept_expr(stmt.expression)

        definition = self.scope.lookup(stmt.identifier)
        check_assignment(stmt.identifier, definition, value.type)

        # it is only possible to assign to runtime definitions, comptime should always be final in this case
        assert isinstance(definition, RuntimeDefinition)

        self.buffer.add(Instruction.new_store(definition.index))
        return False

    def f_statement_block(self, stmt: ast.FStatementBlock) -> bool:
        return self.accept_with_child_scope(stmt.block)

    def f_statement_return(self, stmt: ast.FStatementReturn) -> bool:
        # there should always be a function or root scope available
        sctx = self.scope.find(scopes.Function)
        assert sctx is not None

        if stmt.expression is not None:
            # TODO: warn if returning a value from root

            value = self.accept_expr(stmt.expression)
            sctx.add_return(value.type)
        else:
            self.buffer.add(Instruction(Opcode.NONE))
            sctx.add_return(types.NONE)

        self.buffer.add(Instruction.new_jmp(Opcode.JMP_F, sctx.end))
        return True

    def f_statement_if(self, stmt: ast.FStatementIf) -> bool:
        # evaluate condition
        value = self.accept_expr(stmt.condition)
        check_compatible(stmt.condition, value, types.BOOLEAN)

        # create label for false branch and jmp if false
        label = Label('if_false')
        self.buffer.add(Instruction.new_jmp(Opcode.JMP_FF, label))

        returns = self.accept_with_child_scope(stmt.if_block)

        if stmt.else_block is not None:
            # create unconditional jump to end after true branch
            label_end = Label('if_end')
            self.buffer.add(Instruction.new_jmp(Opcode.JMP_F, label_end))

            # insert label for false branch and
            self.buffer.add_label(label)
            label = label_end

            returns = self.accept_with_child_scope(stmt.else_block) and returns
        else:
            returns = False

        self.buffer.add_label(label)
        return returns

    def f_statement_for(self, stmt: ast.FStatementFor) -> bool:
        sctx = scopes.Loop()

        list_value = self.accept_expr(stmt.condition)
        check_compatible(stmt.condition, list_value, types.ANY_LIST)

        # loop header: create and store iter in unnamed local variable
        list_index = self.allocator.alloc()
        self.buffer.add(Instruction(Opcode.ITER))
        self.buffer.add(Instruction.new_store(list_index))

        # loop start: check if there is a next value
        self.buffer.add_label(sctx.start)
        self.buffer.add(Instruction(Opcode.HAS_NEXT, list_index))
        self.buffer.add(Instruction.new_jmp(Opcode.JMP_FF, sctx.end))

        # loop body: store current value and run block
        self.buffer.add(Instruction(Opcode.NEXT, list_index))
        var_index = self.allocator.alloc()
        self.buffer.add(Instruction.new_store(var_index))

        scope = self.scope.new_child_scope(sctx)
        scope.insert_runtime(stmt.identifier, RuntimeValue(list_value.type.as_scalar), var_index, final=True)

        self.accept_with_scope(scope, stmt.block)

        # loop end: jump back to start
        self.buffer.add(Instruction.new_jmp(Opcode.JMP_B, sctx.start))
        self.buffer.add_label(sctx.end)

        return False

    def f_statement_fail(self, stmt: ast.FStatementFail) -> bool:
        value = self.accept_expr(stmt.expression)
        check_compatible(stmt.expression, value, types.STRING)

        self.buffer.add(Instruction(Opcode.FAIL))
        return True

    def f_statement_expr(self, stmt: ast.FStatementExpr) -> bool:
        self.accept_expr(stmt.expression)
        # TODO: warn if value is not none and unused

        self.buffer.add(Instruction(Opcode.DROP))
        return False

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

        sctx, scope = self.scope.new_call_scope(call.identifier.name)
        for arg, param in zip(call.arguments, func.definition.parameters):
            value = self.accept_expr(arg, load=False)

            if isinstance(value, ComptimeValue):
                scope.insert_comptime(param, value, final=True)
            else:
                definition = scope.insert_runtime(param, value, self.allocator.alloc(), final=True)
                self.buffer.add(Instruction.new_store(definition.index))

        returns = self.accept_with_scope(scope, func.definition.block)

        # if there is no explicit return from the function, insert implicit none
        if not returns:
            self.buffer.add(Instruction(Opcode.NONE))
            sctx.add_return(types.NONE)

        self.buffer.add_label(sctx.end)
        return RuntimeValue(sctx.get_return())

    def expression_call(self, expr: ast.ExpressionCall) -> Value:
        func = resolve_function(self.ctx.file, expr.call.identifier)

        if isinstance(func, BuiltinFunction):
            return self.accept_builtin_function(expr.call, func)

        if isinstance(func, DefinedFunction):
            return self.accept_defined_function(expr.call, func)

        unreachable()

    def expression_list(self, expr: ast.ExpressionList) -> Value:
        # first push empty list to append to
        self.buffer.add(Instruction(Opcode.LIST))

        values: list[Value] = []
        # append all elements
        for element in expr.elements:
            value = self.accept_expr(element)
            self.buffer.add(Instruction(Opcode.APPEND))

            if value.type.is_list:
                fatal_problem('nested lists are not supported', element)

            values.append(value)

        if len(values) == 0:
            return RuntimeValue(types.ANY_LIST)
        else:
            return RuntimeValue(Type.lup(it.type for it in values).as_list)
