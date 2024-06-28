import lark

from .transformer import ASTTransformer
from ..ast import ASTNode

_parser = lark.Lark.open(
    'grammar.lark',
    rel_to=__file__,
    start='start',
    parser='lalr',
    propagate_positions=True,
)


def parse(source: str) -> list[ASTNode]:
    transformer = ASTTransformer()
    return transformer.transform(_parser.parse(source))
