import lark

from ..ast import *


@lark.v_args(meta=True)
class ASTTransformer(lark.Transformer):
    def start(self, meta, children):
        return children

    def parameter(self, meta, children):
        return Parameter(
            meta=meta,
            identifier=str(children[0]),
            type=Type.from_token(children[1]),
        )

    def type_constraint(self, meta, children):
        return TypeConstraint(
            meta=meta,
            identifier=str(children[0]),
            kind=str(children[1]),
            parameter=children[2:-1],
            block=children[-1],
        )

    def main_constraint(self, meta, children):
        return MainConstraint(
            meta=meta,
            block=children[0],
        )

    def block(self, meta, children):
        return Block(
            meta=meta,
            quantifier=Quantifier.from_token(children[0]),
            statements=children[1:],
        )

    def block_statement(self, meta, children):
        return BlockStatement(
            meta=meta,
            block=children[0],
        )

    def attribute_statement(self, meta, children):
        return AttributeStatement(
            meta=meta,
            identifier=str(children[0]),
            comparison=Comparison.from_token(children[1]),
            expression=children[2]
        )

    def reference_statement(self, meta, children):
        return ReferenceStatement(
            meta=meta,
            predicate=children[0],
            reference=children[1],
        )

    def with_statement(self, meta, children):
        return WithStatement(
            meta=meta,
            predicate=children[0],
            kind=str(children[1]),
            block=children[2]
        )

    def int_expr(self, meta, children):
        return LiteralExpression(
            meta=meta,
            type=Type.INTEGER,
            literal=int(children[0]),
        )

    def mul_expr(self, meta, children):
        return BinaryExpression(
            meta=meta,
            type=Type.INTEGER,  # TODO: add type checking
            operator=Operator.MULTIPLICATION,
            left=children[0],
            right=children[1],
        )

    def reference(self, meta, children):
        return Reference(
            meta=meta,
            identifier=str(children[0]),
            arguments=children[1:],
        )

    def int_predicate(self, meta, children):
        return Predicate(
            meta=meta,
            literal=int(children[0]),
        )

    def reference_predicate(self, meta, children):
        return Predicate(
            meta=meta,
            reference=children[0],
        )
