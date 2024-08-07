import typeguard
from typing import Optional

from colc.common import Location, to_snake_case, ComptimeValue

from ._enums import Quantifier, Operator, Comparison, Aggregator, Qualifier


class Node:
    rule: str
    location: Location

    @classmethod
    def _collect_annotations(cls) -> dict[str, type]:
        annotations: dict[str, type] = {}
        for c in cls.__mro__:
            if c != Node:
                annotations.update(getattr(c, '__annotations__', {}))

        return annotations

    def __new__(cls, **kwargs):
        obj = object.__new__(cls)
        obj.rule = to_snake_case(cls.__name__)

        return obj

    def __init__(self, **kwargs):
        for name, t in self._collect_annotations().items():
            value = kwargs.get(name, None)

            try:
                setattr(self, name, typeguard.check_type(value, t))
            except typeguard.TypeCheckError:
                raise TypeError(f'Filed {name} is of type {t}, but got: {value}')

        self.location = kwargs['location']

    def __repr__(self):
        attrs = ', '.join(f'{k}={getattr(self, k)!r}' for k in list(self._collect_annotations()))
        return f'{self.__class__.__name__}[{self.location.start}:{self.location.end}]({attrs})'


class Identifier(Node):
    name: str


class Kind(Node):
    name: str


class String(Node):
    value: str


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
    value: ComptimeValue


class ExpressionRef(Expression):
    identifier: Identifier


class ExpressionAttr(Expression):
    identifier: Identifier
    attribute: Identifier


class ExpressionEmptyList(Expression):
    pass


class Call(Node):
    identifier: Identifier
    arguments: list[Expression]


class Label(Node):
    identifier: Identifier


class ExpressionCall(Expression):
    call: Call


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
    label: Optional[Label]
    predicate: Call
    constraint: Call


class CStatementWith(CStatement):
    label: Optional[Label]
    predicate: Call
    kind: Kind
    block: Optional[CBlock]


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
    kind: Kind
    comparison: Comparison
    expression: Expression


class Definition(Node):
    identifier: Identifier


class CDefinitionType(Definition):
    kind: Kind
    parameters: list[Identifier]
    block: CBlock


class CDefinitionMain(Definition):
    block: CBlock


class PDefinition(Definition):
    parameters: list[Identifier]
    block: PBlock


class FStatement(Node):
    pass


class FBlock(Node):
    statements: list[FStatement]


class FStatementBlock(FStatement):
    block: FBlock


class FStatementDefine(FStatement):
    qualifier: Qualifier
    identifier: Identifier
    expression: Expression


class FStatementAssign(FStatement):
    identifier: Identifier
    expression: Expression


class FStatementReturn(FStatement):
    expression: Optional[Expression]


class FStatementIf(FStatement):
    condition: Expression
    if_block: FBlock
    else_block: Optional[FBlock]


class FStatementFor(FStatement):
    identifier: Identifier
    condition: Expression
    block: FBlock


class FStatementFail(FStatement):
    expression: Expression


class FStatementExpr(FStatement):
    expression: Expression


class FDefinition(Definition):
    parameters: list[Identifier]
    block: FBlock


class MDefinition(Definition):
    block: FBlock
    labels: list[Identifier]


class Include(Node):
    path: String
