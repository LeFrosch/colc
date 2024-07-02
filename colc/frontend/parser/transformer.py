import lark

from ..ast import *


@lark.v_args(meta=True)
class ASTTransformer(lark.Transformer):
    def start(self, meta, children):
        return children

    def parameter(self, meta, children):
        return Parameter(
            meta=meta,
            identifier=children[0],
            type=Type.from_token(children[1]),
        )

    def c_definition_type(self, meta, children):
        return CDefinitionType(
            meta=meta,
            identifier=children[0],
            kind=children[1],
            parameters=children[2:-1],
            block=children[-1],
        )

    def c_definition_main(self, meta, children):
        return CDefinitionMain(
            meta=meta,
            identifier=children[0],
            block=children[1],
        )

    def c_block(self, meta, children):
        return CBlock(
            meta=meta,
            quantifier=Quantifier.from_token(children[0]),
            statements=children[1:],
        )

    def c_statement_block(self, meta, children):
        return CStatementBlock(
            meta=meta,
            block=children[0],
        )

    def c_statement_attr(self, meta, children):
        return CStatementAttr(
            meta=meta,
            identifier=children[0],
            comparison=Comparison.from_token(children[1]),
            expression=children[2]
        )

    def c_statement_call(self, meta, children):
        return CStatementCall(
            meta=meta,
            predicate=children[0],
            constraint=children[1],
        )

    def c_statement_with(self, meta, children):
        return CStatementWith(
            meta=meta,
            predicate=children[0],
            kind=children[1],
            block=children[2]
        )

    def p_definition(self, meta, children):
        return PDefinition(
            meta=meta,
            identifier=children[0],
            parameters=children[1:-1],
            block=children[-1],
        )

    def p_block(self, meta, children):
        return PBlock(
            meta=meta,
            quantifier=Quantifier.from_token(children[0]),
            statements=children[1:],
        )

    def p_statement_block(self, meta, children):
        return PStatementBlock(
            meta=meta,
            block=children[0],
        )

    def p_statement_size(self, meta, children):
        return PStatementSize(
            meta=meta,
            comparison=Comparison.from_token(children[0]),
            expression=children[1],
        )

    def p_statement_aggr(self, meta, children):
        return PStatementAggr(
            meta=meta,
            aggregator=Aggregator.from_token(children[0]),
            kind=children[1],
            comparison=Comparison.from_token(children[2]),
            expression=children[3],
        )

    def expression_int(self, meta, children):
        return ExpressionLiteral(
            meta=meta,
            type=Type.INTEGER,
            literal=int(children[0]),
        )

    def expression_str(self, meta, children):
        return ExpressionLiteral(
            meta=meta,
            type=Type.STRING,
            literal=str(children[0][1:-1]),
        )

    def expression_ref(self, meta, children):
        return ExpressionRef(
            meta=meta,
            identifier=children[0],
        )

    def expression_mul(self, meta, children):
        return ExpressionBinary(
            meta=meta,
            operator=Operator.MULTIPLICATION,
            left=children[0],
            right=children[1],
        )

    def call(self, meta, children):
        return Call(
            meta=meta,
            identifier=children[0],
            arguments=children[1:],
        )
