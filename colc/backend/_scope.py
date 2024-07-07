import dataclasses
from typing import Optional, Any

from colc.common import fatal_problem
from colc.frontend import ast, Visitor, Type

from ._typing import CompiletimeValue, type_from_value


@dataclasses.dataclass
class Definition:
    index: int
    identifier: ast.Identifier
    type: Type
    value: Optional[CompiletimeValue]

    def __post_init__(self):
        if self.value is not None:
            assert self.type == type_from_value(self.value)


class Scope:
    def __init__(self, parent: Optional['Scope'] = None):
        self._parent = parent
        self._declarations: list[Definition] = []

        if parent is None:
            self._offset = 0
        else:
            self._offset = parent._offset + len(parent._declarations)

    def define(self, identifier: ast.Identifier, type: Type, value: Optional[CompiletimeValue] = None) -> Definition:
        definition = next(filter(lambda it: it.identifier.name == identifier.name, self._declarations), None)

        if definition is not None:
            fatal_problem('identifier is already defined', identifier)

        definition = Definition(self._offset + len(self._declarations), identifier, type, value)
        self._declarations.append(definition)

        return definition

    def lookup(self, identifier: ast.Identifier) -> Definition:
        definition = next(filter(lambda it: it.identifier.name == identifier.name, self._declarations), None)

        if definition is not None:
            return definition
        if self._parent is not None:
            return self._parent.lookup(identifier)

        fatal_problem('undefined identifier', identifier)

    def new_child_scope(self) -> 'Scope':
        return Scope(self._parent)


class VisitorWithScope(Visitor):
    def __init__(self):
        super().__init__()
        self.scope = Scope()

    def accept_with_scope(self, scope: Scope, node: Optional[ast.Node]) -> Any:
        current_scope = self.scope

        self.scope = scope
        result = self.accept(node)
        self.scope = current_scope

        return result
