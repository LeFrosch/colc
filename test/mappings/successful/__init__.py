import unittest

from colc import Instruction, Config
from test.utils import FileTestMeta, compile_mappings


# TODO: add compile time value type
def _format_pool_entry(index: int, value):
    return '%03d: %s' % (index, value)


def _format_instruction(index: int, instruction: Instruction):
    return '%03d: %-10s %d' % (
        index,
        instruction.opcode.name,
        instruction.argument,
    )


class FileTest(unittest.TestCase, metaclass=FileTestMeta, path=__file__):
    def do_test(self, input, output, const_pool=None, optimizations=''):
        config = Config(optimizations=optimizations.split('\n'))
        ctx, mappings = compile_mappings(input, config)
        self.assertGreater(len(mappings), 0)

        mapping = next(iter(mappings.values()))

        expected_output = '\n'.join(_format_instruction(i, it) for i, it in enumerate(mapping))
        self.assertEqual(output, expected_output)

        if const_pool:
            expected_pool = '\n'.join(_format_pool_entry(i, it) for i, it in enumerate(ctx.const_pool))
            self.assertEqual(const_pool, expected_pool)
