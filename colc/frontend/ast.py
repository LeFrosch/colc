import re
import typeguard

from .text import Location
from .enums import Quantifier, Operator, Comparison, Aggregator, Type


def _to_snake_case(name):
    """
    Converts a name from camelCase to snake_case.
    Source: https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


class Node:
    location: Location

    def _collect_annotations(self) -> dict[str, type]:
        annotations = {}
        for c in self.__class__.__mro__:
            annotations.update(getattr(c, '__annotations__', {}))

        return annotations

    def __new__(cls, **kwargs):
        obj = object.__new__(cls)
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
        attrs = ', '.join(f'{k}={getattr(self, k)!r}' for k in list(self._collect_annotations()) if k != 'location')
        return f'{self.__class__.__name__}[{self.location.start}:{self.location.end}]({attrs})'


class Identifier(Node):
    name: str


class String(Node):
    value: str


class Parameter(Node):
    identifier: Identifier
    type: Type


class Expression(Node):
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
    identifier: Identifier


class Call(Node):
    identifier: Identifier
    arguments: list[Expression]


class CStatement(Node):
    pass


class CBlock(Node):
    quantifier: Quantifier
    statements: list[CStatement]


class CStatementBlock(CStatement):
    block: CBlock


class CStatementAttr(CStatement):
    identifier: Identifier
    comparison: Comparison
    expression: Expression


class CStatementCall(CStatement):
    predicate: Call
    constraint: Call


class CStatementWith(CStatement):
    predicate: Call
    kind: Identifier
    block: CBlock | None


class PStatement(Node):
    pass


class PBlock(Node):
    quantifier: Quantifier
    statements: list[PStatement]


class PStatementBlock(PStatement):
    block: PBlock


class PStatementSize(PStatement):
    comparison: Comparison
    expression: Expression


class PStatementAggr(PStatement):
    aggregator: Aggregator
    kind: Identifier
    comparison: Comparison
    expression: Expression


class Definition(Node):
    identifier: Identifier


class CDefinitionType(Definition):
    kind: Identifier
    parameters: list[Parameter]
    block: CBlock


class CDefinitionMain(Definition):
    block: CBlock


class PDefinition(Definition):
    parameters: list[Parameter]
    block: PBlock


class FStatement(Node):
    pass


class FBlock(Node):
    statements: list[FStatement]


class FStatementBlock(FStatement):
    block: FBlock


class FStatementAssign(FStatement):
    identifier: Identifier
    expression: Expression


class FStatementReturn(FStatement):
    expression: Expression


class FDefinition(Definition):
    identifier: Identifier
    parameters: list[Parameter]
    block: FBlock


class Include(Node):
    path: String
