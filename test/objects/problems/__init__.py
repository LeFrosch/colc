import unittest

from colc import FatalProblem
from test.utils import FileTestMeta, compile_object


class FileTest(unittest.TestCase, metaclass=FileTestMeta, path=__file__):
    def do_test(self, input: str, output: str):
        try:
            compile_object(input)
            self.fail('expected a fatal problem')
        except FatalProblem as e:
            self.assertEqual(output, e.render())
