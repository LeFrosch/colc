import pathlib
import unittest

from colc import TextFile, parse_file, Instruction
from colc.backend import process_mapping, Context

from test.utils import FileTestMeta


def _format_instruction(index: int, instruction: Instruction):
    return '%03d: %-10s %d' % (
        index,
        instruction.opcode.name,
        instruction.argument,
    )


class MappingTest(unittest.TestCase, metaclass=FileTestMeta, path=__file__):
    def do_test(self, input: str, output: str):
        file = parse_file(TextFile(pathlib.Path('test.col'), input))
        result = process_mapping(Context(file), file.mappings[0])

        expected = '\n'.join(_format_instruction(i, it) for (i, it) in enumerate(result))
        self.assertEqual(output, expected)
