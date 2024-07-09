import unittest

from colc import Config, debug
from test.utils import FileTestMeta, compile_mappings


class FileTest(unittest.TestCase, metaclass=FileTestMeta, path=__file__):
    def do_test(self, input, output, const_pool=None, optimizations=''):
        config = Config(optimizations=optimizations.split('\n'))
        ctx, mappings = compile_mappings(input, config)
        self.assertGreater(len(mappings), 0)

        mapping = next(iter(mappings.values()))
        self.assertEqual(output, debug.format_instructions(mapping))

        if const_pool:
            self.assertEqual(const_pool, debug.format_pool(ctx.const_pool))
