import unittest

from colc import FatalProblem
from test.utils import FileTestMeta, compile_mappings


class FileTest(unittest.TestCase, metaclass=FileTestMeta, path=__file__):
    def do_test(self, input: str, output: str):
        try:
            compile_mappings(input)
            self.fail('expected a fatal problem')
        except FatalProblem as e:
            self.assertEqual(output, e.render())
