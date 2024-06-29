import re
import lark
import typeguard

from .type import Type
from .enums import Quantifier, Operator, Comparison, Aggregator


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
    pass


class ExpressionBinary(Expression):
    operator: Operator
    left: Expression
    right: Expression


class ExpressionUnary(Expression):
    operator: Operator
    expression: Expression


class ExpressionLiteral(Expression):
    literal: int | str
    type: Type


class ExpressionRef(Expression):
    identifier: str


class Call(ASTNode):
    identifier: str
    arguments: list[Expression]


class CStatement(ASTNode):
    pass


class CBlock(ASTNode):
    quantifier: Quantifier
    statements: list[CStatement]


class CStatementBlock(CStatement):
    block: CBlock


class CStatementAttr(CStatement):
    identifier: str
    comparison: Comparison
    expression: Expression


class CStatementCall(CStatement):
    predicate: Call
    constraint: Call


class CStatementWith(CStatement):
    predicate: Call
    kind: str
    block: CBlock | None


class PStatement(ASTNode):
    pass


class PBlock(ASTNode):
    quantifier: Quantifier
    statements: list[PStatement]


class PStatementBlock(PStatement):
    block: PBlock


class PStatementSize(PStatement):
    comparison: Comparison
    expression: Expression


class PStatementAggr(PStatement):
    aggregator: Aggregator
    kind: str
    comparison: Comparison
    expression: Expression


class Definition(ASTNode):
    pass


class CDefinitionType(Definition):
    identifier: str
    kind: str
    parameters: list[Parameter]
    block: CBlock


class CDefinitionMain(Definition):
    block: CBlock


class PDefinition(Definition):
    identifier: str
    parameters: list[Parameter]
    block: PBlock


class FStatement(ASTNode):
    pass


class FBlock(ASTNode):
    statements: list[FStatement]


class FStatementBlock(FStatement):
    block: FBlock


class FStatementAssign(FStatement):
    identifier: str
    expression: Expression


class FStatementReturn(FStatement):
    expression: Expression


class FDefinition(Definition):
    identifier: str
    parameters: list[Parameter]
    block: FBlock
