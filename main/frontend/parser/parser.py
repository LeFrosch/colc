import lark

import problems
from .transformer import ASTTransformer
from ..ast import ASTNode

_parser = lark.Lark.open(
    'grammar.lark',
    rel_to=__file__,
    start='start',
    parser='lalr',
    propagate_positions=True,
)


def parse(text: str) -> list[ASTNode]:
    transformer = ASTTransformer()

    try:
        return transformer.transform(_parser.parse(text))
    except lark.UnexpectedToken as e:
        if e.token.type == '$END':
            problems.report_fatal('unexpected end of input')
        else:
            problems.report_fatal('unexpected token', problems.location_from_token(e.token))
    except lark.UnexpectedCharacters as e:
        problems.report_fatal('unexpected character', problems.location_from_pos(e.line, e.column))
    except lark.UnexpectedEOF as e:
        problems.report_fatal('unexpected end of input')
    except Exception as e:
        problems.report_internal('unexpected lark exception', e)

