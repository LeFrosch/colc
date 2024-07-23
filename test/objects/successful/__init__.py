import pathlib
import unittest

from colc import Object, FatalProblem
from test.utils import compile_object


class ObjectTest(unittest.TestCase):
    def __init__(self, *args):
        super().__init__(*args)
        self.dir = pathlib.Path(__file__).parent

    def compile(self, file: str) -> Object:
        text = self.dir.joinpath(f'{file}.col').read_text()

        try:
            (_, obj) = compile_object(text)
        except FatalProblem as e:
            self.fail(e.render())

        return obj

    def test_label(self):
        obj = self.compile('label')

        self.assertEqual([0], obj.mappings[0].labels)
        self.assertEqual([], obj.mappings[1].labels)

    def test_all(self):
        self.compile('all')
