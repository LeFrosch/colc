import unittest

from colc.common import first

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

        mapping = first(mappings)
        self.assertEqual(output, debug.format_instructions(mapping.code))

        if const_pool:
            self.assertEqual(const_pool, debug.format_pool(ctx.get_const_pool()))
        else:
            self.assertEqual(len(ctx.get_const_pool()), 0)
