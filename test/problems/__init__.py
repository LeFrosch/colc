import unittest

from utils import FileTestMeta

from colc.problems import FatalProblem
from colc.frontend import parse
from colc.backend import process


class ProblemTest(unittest.TestCase, metaclass=FileTestMeta, path=__file__):
    def do_test(self, input: str, output: str):
        try:
            process(parse(input))
            self.fail('should throw a fatal problem')
        except FatalProblem as e:
            self.assertEqual(output, e.render(input))
