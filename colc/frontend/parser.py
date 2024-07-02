import lark

from .text import TextFile
from .ast import *


@lark.v_args(meta=True)
class Transformer(lark.Transformer):
    def __init__(self, file: TextFile):
        self.file = file

    def location_from_meta(self, meta: lark.tree.Meta) -> Location:
        return Location(
            file=self.file,
            start=meta.start_pos,
            end=meta.end_pos,
        )

    def location_from_token(self, token: lark.Token) -> Location:
        return Location(
            file=self.file,
            start=token.start_pos,
            end=token.end_pos,
        )

    def identifier_from_token(self, token: lark.Token) -> Identifier:
        return Identifier(
            location=self.location_from_token(token),
            name=token.value,
        )

    def string_from_token(self, token: lark.Token) -> String:
        return String(
            location=self.location_from_token(token),
            value=token.value[1:-1],
        )


    def start(self, meta, children):
        return children

    def include(self, meta, children):
        return Include(
            location=self.location_from_meta(meta),
            path=self.string_from_token(children[0]),
        )

    def parameter(self, meta, children):
        return Parameter(
            location=self.location_from_meta(meta),
            identifier=self.identifier_from_token(children[0]),
            type=Type.from_token(children[1]),
        )

    def c_definition_type(self, meta, children):
        return CDefinitionType(
            location=self.location_from_meta(meta),
            identifier=self.identifier_from_token(children[0]),
            kind=self.identifier_from_token(children[1]),
            parameters=children[2:-1],
            block=children[-1],
        )

    def c_definition_main(self, meta, children):
        return CDefinitionMain(
            location=self.location_from_meta(meta),
            identifier=self.identifier_from_token(children[0]),
            block=children[1],
        )

    def c_block(self, meta, children):
        return CBlock(
            location=self.location_from_meta(meta),
            quantifier=Quantifier.from_token(children[0]),
            statements=children[1:],
        )

    def c_statement_block(self, meta, children):
        return CStatementBlock(
            location=self.location_from_meta(meta),
            block=children[0],
        )

    def c_statement_attr(self, meta, children):
        return CStatementAttr(
            location=self.location_from_meta(meta),
            identifier=self.identifier_from_token(children[0]),
            comparison=Comparison.from_token(children[1]),
            expression=children[2],
        )

    def c_statement_call(self, meta, children):
        return CStatementCall(
            location=self.location_from_meta(meta),
            predicate=children[0],
            constraint=children[1],
        )

    def c_statement_with(self, meta, children):
        return CStatementWith(
            location=self.location_from_meta(meta),
            predicate=children[0],
            kind=self.identifier_from_token(children[1]),
            block=children[2],
        )

    def p_definition(self, meta, children):
        return PDefinition(
            location=self.location_from_meta(meta),
            identifier=self.identifier_from_token(children[0]),
            parameters=children[1:-1],
            block=children[-1],
        )

    def p_block(self, meta, children):
        return PBlock(
            location=self.location_from_meta(meta),
            quantifier=Quantifier.from_token(children[0]),
            statements=children[1:],
        )

    def p_statement_block(self, meta, children):
        return PStatementBlock(
            location=self.location_from_meta(meta),
            block=children[0],
        )

    def p_statement_size(self, meta, children):
        return PStatementSize(
            location=self.location_from_meta(meta),
            comparison=Comparison.from_token(children[0]),
            expression=children[1],
        )

    def p_statement_aggr(self, meta, children):
        return PStatementAggr(
            location=self.location_from_meta(meta),
            aggregator=Aggregator.from_token(children[0]),
            kind=children[1],
            comparison=Comparison.from_token(children[2]),
            expression=children[3],
        )

    def expression_int(self, meta, children):
        return ExpressionLiteral(
            location=self.location_from_meta(meta),
            type=Type.INTEGER,
            literal=int(children[0]),
        )

    def expression_str(self, meta, children):
        return ExpressionLiteral(
            location=self.location_from_meta(meta),
            type=Type.STRING,
            literal=str(children[0][1:-1]),
        )

    def expression_ref(self, meta, children):
        return ExpressionRef(
            location=self.location_from_meta(meta),
            identifier=self.identifier_from_token(children[0]),
        )

    def expression_mul(self, meta, children):
        return ExpressionBinary(
            location=self.location_from_meta(meta),
            operator=Operator.MULTIPLICATION,
            left=children[0],
            right=children[1],
        )

    def call(self, meta, children):
        return Call(
            location=self.location_from_meta(meta),
            identifier=self.identifier_from_token(children[0]),
            arguments=children[1:],
        )


_parser = lark.Lark.open(
    'grammar.lark',
    rel_to=__file__,
    start='start',
    parser='lalr',
    propagate_positions=True,
)


def parse(file: TextFile) -> list[Node]:
    return Transformer(file).transform(_parser.parse(file.text))
