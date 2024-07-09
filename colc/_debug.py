from colc.common import StringBuilder
from colc.backend import Instruction

from ._object import Object


def format_pool(values: list) -> str:
    builder = StringBuilder()

    for i, value in enumerate(values):
        builder.write_line('%03d: %s' % (i, value))

    return builder.build()


def _format_instruction(index: int, instruction: Instruction) -> str:
    string = '%03d: %-8s %3d' % (
        index,
        instruction.opcode.name,
        instruction.argument,
    )

    if instruction.debug is not None:
        string += ' = (%s)' % instruction.debug

    return string


def format_instructions(instructions: list[Instruction]) -> str:
    builder = StringBuilder()

    for i, instruction in enumerate(instructions):
        builder.write_line(_format_instruction(i, instruction))

    return builder.build()


def print_debug_info(obj: Object):
    print('CONSTRAINT:')
    print(repr(obj.constraint))
    print()

    if len(obj.const_pool) > 0:
        print('CONST POOL:')
        print(format_pool(obj.const_pool))
        print()

    for name, instructions in obj.mappings.items():
        print('MAPPING: %s' % name)
        print(format_instructions(instructions))
        print()
