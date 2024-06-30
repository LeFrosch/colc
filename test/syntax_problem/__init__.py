import unittest
import problems

from utils import FileTestMeta

from frontend import parse


class ConstraintTest(unittest.TestCase, metaclass=FileTestMeta, path=__file__):
    def do_test(self, input: str, output: str):
        try:
            parse(input)
            self.fail('parsing should throw a fatal problem')
        except problems.FatalProblem as e:
            self.assertEqual(output, e.render(input))

