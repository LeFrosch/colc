import typing

from colc.common import fatal_problem, internal_problem
from colc.frontend import ast, Visitor, Operator

from ._context import Context
from ._instruction import Instruction, Opcode


def process_mapping(ctx: Context, mapping: ast.MDefinition) -> list[Instruction]:
    visitor = VisitorImpl(ctx)
    visitor.accept(mapping.block)

    return visitor.instructions


# TODO: can this be merged with the scope which is used for constraint evaluation?
class Scope:
    def __init__(self, parent: typing.Optional['Scope'] = None):
        self._parent = parent
        self._offset = parent.size if parent else 0
        self._local_variables: list[str] = []

    @property
    def size(self) -> int:
        return len(self._local_variables)

    def declare(self, identifier: ast.Identifier) -> int:
        name = identifier.name

        if name in self._local_variables:
            local_index = self._local_variables.index(name)
        else:
            self._local_variables.append(name)
            local_index = len(self._local_variables) - 1

        return self._offset + local_index

    def lookup(self, identifier: ast.Identifier) -> int:
        name = identifier.name

        if name in self._local_variables:
            return self._local_variables.index(name) + self._offset
        if self._parent:
            return self._parent.lookup(identifier)

        fatal_problem('undefined identifier', identifier)

    def push(self) -> 'Scope':
        return Scope(parent=self)

    def pop(self) -> 'Scope':
        if not self._parent:
            internal_problem('cannot pop root scope')

        return self._parent


class VisitorImpl(Visitor):
    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.scope = Scope()
        self.instructions: list[Instruction] = []

    def f_block(self, block: ast.FBlock):
        self.accept_all(block.statements)

    def f_statement_assign(self, stmt: ast.FStatementAssign):
        self.accept(stmt.expression)

        index = self.scope.declare(stmt.identifier)
        self.instructions.append(Opcode.I_STORE.new(index))

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
