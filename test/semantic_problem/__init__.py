import unittest

from utils import FileTestMeta

from colc.problems import FatalProblem
from colc.frontend import parse
from colc.backend.file import File
from colc.backend.constraint import process_constraint


class SemanticProblemTest(unittest.TestCase, metaclass=FileTestMeta, path=__file__):
    def do_test(self, input: str, output: str):
        file = File(parse(input))

        try:
            process_constraint(file)
            self.fail('processing should throw a fatal problem')
        except FatalProblem as e:
            self.assertEqual(output, e.render(input))
