import lark

from .transformer import ASTTransformer
from .file import File

_parser = lark.Lark.open(
    'grammar.lark',
    rel_to=__file__,
    start='start',
    parser='lalr',
    propagate_positions=True,
)


def parse(source: str) -> File:
    transformer = ASTTransformer()

    definitions = transformer.transform(_parser.parse(source))

    return File(definitions=definitions)
