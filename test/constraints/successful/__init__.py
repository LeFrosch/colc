import unittest

from colc import Config, FatalProblem
from test.utils import FileTestMeta, compile_constraint


class FileTest(unittest.TestCase, metaclass=FileTestMeta, path=__file__):
    def do_test(self, input: str, output: str, optimizations=''):
        config = Config(optimizations=optimizations.split('\n'))

        try:
            _, constraint = compile_constraint(input, config)
        except FatalProblem as e:
            self.fail(e.render())

        self.assertEqual(output, repr(constraint))
