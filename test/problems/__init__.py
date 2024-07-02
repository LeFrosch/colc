import pathlib
import unittest
import colc

from test.utils import FileTestMeta



class ProblemTest(unittest.TestCase, metaclass=FileTestMeta, path=__file__):
    def do_test(self, input: str, output: str):
        try:
            colc.compile_file(colc.TextFile(pathlib.Path('test.col'), input))
            self.fail('should throw a fatal problem')
        except colc.problems.FatalProblem as e:
            self.assertEqual(output, e.render())
