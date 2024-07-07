import unittest

from colc import Instruction
from test.utils import FileTestMeta, compile_mappings


def _format_instruction(index: int, instruction: Instruction):
    return '%03d: %-10s %d' % (
        index,
        instruction.opcode.name,
        instruction.argument,
    )


class FileTest(unittest.TestCase, metaclass=FileTestMeta, path=__file__):
    def do_test(self, input: str, output: str):
        mappings = compile_mappings(input)
        self.assertGreater(len(mappings), 0)

        mapping = next(iter(mappings.values()))

        expected = '\n'.join(_format_instruction(i, it) for (i, it) in enumerate(mapping))
        self.assertEqual(output, expected)
