import unittest

from colc import Config
from test.utils import FileTestMeta, compile_constraint


class FileTest(unittest.TestCase, metaclass=FileTestMeta, path=__file__):
    def do_test(self, input: str, output: str, optimizations=''):
        config = Config(optimizations=optimizations.split('\n'))
        _, constraint = compile_constraint(input, config)
        self.assertEqual(output, repr(constraint))
