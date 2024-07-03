import pathlib
import unittest

from colc import FatalProblem, TextFile, compile_file
from test.utils import FileTestMeta


class ProblemTest(unittest.TestCase, metaclass=FileTestMeta, path=__file__):
    def do_test(self, input: str, output: str):
        try:
            compile_file(TextFile(pathlib.Path('test.col'), input))
            self.fail('should throw a fatal problem')
        except FatalProblem as e:
            self.assertEqual(output, e.render())
