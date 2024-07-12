import unittest

from colc import Config, debug, FatalProblem
from test.utils import FileTestMeta, compile_mappings


class FileTest(unittest.TestCase, metaclass=FileTestMeta, path=__file__):
    def do_test(self, input, output, const_pool=None, optimizations=''):
        config = Config(optimizations=optimizations.split('\n'))

        try:
            ctx, mappings = compile_mappings(input, config)
        except FatalProblem as e:
            self.fail(e.render())

        self.assertGreater(len(mappings), 0)

        mapping = next(iter(mappings.values()))
        self.assertEqual(output, debug.format_instructions(mapping))

        if const_pool:
            self.assertEqual(const_pool, debug.format_pool(ctx._const_pool))
        else:
            self.assertEqual(len(ctx._const_pool), 0)
