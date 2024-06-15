import re
import lark
import typeguard

from .type import Type
from .enums import Quantifier, Operator, Comparison


def _to_snake_case(name):
    """
    Converts a name from camelCase to snake_case.
    Source: https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


class ASTNode:
    meta: lark.tree.Meta

    def _collect_annotations(self) -> dict[str, type]:
        annotations = {}
        for c in self.__class__.__mro__:
            annotations.update(getattr(c, '__annotations__', {}))

        return annotations

    def __new__(cls, **kwargs):
        obj = object.__new__(cls)
        obj.name = cls.__name__
        obj.rule = _to_snake_case(cls.__name__)

        return obj

    def __init__(self, **kwargs):
        for name, t in self._collect_annotations().items():
            value = kwargs.get(name, None)

            try:
                setattr(self, name, typeguard.check_type(value, t))
            except typeguard.TypeCheckError:
                raise TypeError(f'Filed {name} is of type {t}, but got: {value}')

    def __repr__(self):
        attributes = ', '.join(f'{k}={getattr(self, k)!r}' for k in list(self._collect_annotations()) if k != 'meta')
        return f'{self.name}[{self.meta.start_pos}:{self.meta.end_pos}]({attributes})'


class Parameter(ASTNode):
    identifier: str
    type: Type


class Expression(ASTNode):
    type: Type


class BinaryExpression(Expression):
    operator: Operator
    left: Expression
    right: Expression


class UnaryExpression(Expression):
    operator: Operator
    expression: Expression


class LiteralExpression(Expression):
    literal: int | str


class Reference(ASTNode):
    identifier: int
    arguments: list[Expression]


class Predicate(ASTNode):
    literal: int | None
    reference: Reference | None


class Statement(ASTNode):
    pass


class Block(ASTNode):
    quantifier: Quantifier
    statements: list[Statement]


class BlockStatement(Statement):
    block: Block


class AttributeStatement(Statement):
    identifier: str
    comparison: Comparison
    expression: Expression


class ReferenceStatement(Statement):
    predicate: Predicate
    reference: Reference


class WithStatement(Statement):
    predicate: Predicate
    kind: str
    block: Block | None


class TypeConstraint(ASTNode):
    identifier: str
    kind: str
    parameter: list[Parameter]
    block: Block


class MainConstraint(ASTNode):
    block: Block
