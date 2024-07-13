from typing import Iterable, Tuple

from colc.common import fatal_problem, Type
from colc.frontend import ast

from ._instruction import Instruction, Opcode
from ._scope import Definition


class Allocator:
    def __init__(self):
        self.index: int = 0

    def alloc(self) -> int:
        self.index += 1
        return self.index - 1


class JmpAnchor:
    def __init__(self, instructions: list[Instruction], opcode: Opcode):
        self._instructions = instructions
        self._instruction = opcode.new(0)

        instructions.append(self._instruction)
        self._address = len(instructions)

    def set_address(self):
        offset = len(self._instructions) - self._address
        assert 0 < offset < 265

        self._instruction.argument = offset
        self._instruction.debug = str(len(self._instructions))


def zip_call_arguments(call: ast.Call, target) -> Iterable[Tuple[ast.Expression, ast.Identifier]]:
    arguments = call.arguments
    parameters = target.parameters

    if len(arguments) < len(parameters):
        fatal_problem('not enough arguments', call.identifier)
    if len(arguments) > len(parameters):
        fatal_problem('too many arguments', call.identifier)

    return zip(arguments, parameters)


def check_assignment(identifier: ast.Identifier, definition: Definition, type: Type):
    if definition.final:
        fatal_problem('cannot assign to final identifier', identifier)
    if not definition.value.type.compatible(type):
        fatal_problem(f'cannot assign {type} to {definition.value} identifier', identifier)
