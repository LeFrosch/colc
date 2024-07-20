from colc.common import StringBuilder
from colc.backend import Opcode

from ._object import Object


def format_pool(values: list) -> str:
    builder = StringBuilder()

    for i, value in enumerate(values):
        builder.write_line('%03d: %s' % (i, value))

    return builder.build()


def format_code(buffer: bytes) -> str:
    builder = StringBuilder()

    for i in range(0, len(buffer) // 2):
        line = '%03d: %-8s %3d' % (
            i,
            Opcode(buffer[i * 2]).name,
            buffer[i * 2 + 1],
        )
        builder.write_line(line)

    return builder.build()


def print_debug_info(obj: Object):
    print('CONSTRAINT:')
    print(repr(obj.constraint))
    print()

    if len(obj.const_pool) > 0:
        print('CONST POOL:')
        print(format_pool(obj.const_pool))
        print()

    for mapping in obj.mappings:
        print('MAPPING: %s' % mapping.name)
        print(format_code(mapping.code))
        print()
