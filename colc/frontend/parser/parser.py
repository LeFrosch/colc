import lark

from colc.problems import fatal_problem, internal_problem
from colc.frontend.ast import ASTNode

from .transformer import ASTTransformer

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
            fatal_problem('unexpected end of input')
        else:
            fatal_problem('unexpected token', at_token=e.token)
    except lark.UnexpectedCharacters as e:
        fatal_problem('unexpected character', at_pos=(e.line, e.column))
    except lark.UnexpectedEOF:
        fatal_problem('unexpected end of input')
    except Exception as e:
        internal_problem('unexpected lark exception', e)
