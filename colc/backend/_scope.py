import dataclasses
import abc
from typing import Optional, Any

from colc.common import fatal_problem, internal_problem, Value, RuntimeValue, ComptimeValue, Type, first
from colc.frontend import ast, Visitor


@dataclasses.dataclass
class Definition(abc.ABC):
    name: str
    final: bool
    value: Value

    @property
    @abc.abstractmethod
    def is_comptime(self) -> bool: ...

    @property
    def is_runtime(self) -> bool:
        return not self.is_comptime


@dataclasses.dataclass
class RuntimeDefinition(Definition):
    value: RuntimeValue
    index: int

    @property
    def is_comptime(self) -> bool:
        return False


@dataclasses.dataclass
class ComptimeDefinition(Definition):
    value: ComptimeValue

    @property
    def is_comptime(self) -> bool:
        return True


class Scope:
    def __init__(self, parent: Optional['Scope']):
        self._parent = parent
        self._definitions: list[Definition] = []

    def _insert(self, identifier: ast.Identifier, definition: Definition):
        if any(it for it in self._definitions if it.name == identifier.name):
            fatal_problem('identifier is already defined', identifier)
        if definition.value.type.is_none:
            fatal_problem('cannot assign <none>', identifier)

        self._definitions.append(definition)

    def insert_comptime(self, identifier: ast.Identifier, value: ComptimeValue, final: bool) -> ComptimeDefinition:
        definition = ComptimeDefinition(identifier.name, final, value)
        self._insert(identifier, definition)

        return definition

    def insert_runtime(self, identifier: ast.Identifier, value: Value, index: int, final: bool) -> RuntimeDefinition:
        definition = RuntimeDefinition(identifier.name, final, value.as_runtime, index)
        self._insert(identifier, definition)

        return definition

    def insert_synthetic(self, name: str, type: Type, index: int) -> RuntimeDefinition:
        definition = RuntimeDefinition(name, True, RuntimeValue(type), index)

        if any(it for it in self._definitions if it.name == name):
            internal_problem(f'identifier is already defined {name}')
        self._definitions.append(definition)

        return definition

    def lookup(self, identifier: ast.Identifier, expected: Optional[Type] = None) -> Definition:
        definition = first(it for it in self._definitions if it.name == identifier.name)

        if definition is None and self._parent is not None:
            definition = self._parent.lookup(identifier)
        if definition is None:
            fatal_problem('undefined identifier', identifier)

        if expected is not None and not definition.value.type.compatible(expected):
            fatal_problem(f'identifier {definition.value.type} not compatible with {expected}', identifier)

        return definition

    def new_call_scope(self) -> 'Scope':
        return Scope(None)

    def new_child_scope(self) -> 'Scope':
        return Scope(self)


class VisitorWithScope(Visitor):
    def __init__(self, scope: Optional[Scope] = None):
        super().__init__()
        self.scope = scope or Scope(None)

    def accept_with_scope(self, scope: Scope, node: Optional[ast.Node]) -> Any:
        current_scope = self.scope

        self.scope = scope
        result = self.accept(node)
        self.scope = current_scope

        return result

    def accept_with_child_scope(self, node: Optional[ast.Node]) -> Any:
        return self.accept_with_scope(self.scope.new_child_scope(), node)
