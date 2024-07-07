import dataclasses
from typing import Optional, Any

from colc.common import fatal_problem, internal_problem
from colc.frontend import ast, Visitor, Value


@dataclasses.dataclass
class Definition:
    index: int
    name: str
    value: Value

    @property
    def is_comptime(self):
        return self.value.is_comptime


class Scope:
    def __init__(self, parent: Optional['Scope'] = None):
        self._parent = parent
        self._definitions: list[Definition] = []

        if parent is None:
            self._offset = 0
        else:
            self._offset = parent._offset + len(parent._definitions)

    def _find_definition(self, name: str) -> Optional[Definition]:
        return next((it for it in self._definitions if it.name == name), None)

    def define(self, identifier: ast.Identifier, value: Value = Value.default()) -> Definition:
        definition = self._find_definition(identifier.name)

        if definition is not None:
            fatal_problem('identifier is already defined', identifier)

        definition = Definition(self._offset + len(self._definitions), identifier.name, value)
        self._definitions.append(definition)

        return definition

    def define_synthetic(self, name: str, value: Value = Value.default()) -> Definition:
        definition = self._find_definition(name)

        if definition is not None:
            internal_problem(f'synthetic identifier is already defined {name}')

        definition = Definition(self._offset + len(self._definitions), name, value)
        self._definitions.append(definition)

        return definition

    def lookup(self, identifier: ast.Identifier) -> Definition:
        definition = self._find_definition(identifier.name)

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
