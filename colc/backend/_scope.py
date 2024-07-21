import dataclasses
import abc
from typing import Optional, Any, Tuple, TypeVar

from colc.common import fatal_problem, internal_problem, Value, RuntimeValue, ComptimeValue, Type, first
from colc.frontend import ast, Visitor

from . import _scope_context as scopes


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


C = TypeVar('C', bound=scopes.Context)


class Scope:
    def __init__(self, parent: Optional['Scope'], ctx: Optional[scopes.Context]):
        self._parent = parent
        self._definitions: list[Definition] = []
        self._context = ctx

    def _insert(self, identifier: ast.Identifier, definition: Definition):
        if any(it for it in self._definitions if it.name == identifier.name):
            fatal_problem('identifier is already defined', identifier)

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

    def find(self, context_type: type[C]) -> Optional[C]:
        if isinstance(self._context, context_type):
            return self._context

        if self._parent is not None:
            return self._parent.find(context_type)

        return None

    def new_call_scope(self, name: str) -> Tuple[scopes.Function, 'Scope']:
        ctx = scopes.Function(name)
        return ctx, Scope(None, ctx)

    def new_child_scope(self, ctx: Optional[scopes.Context] = None) -> 'Scope':
        return Scope(self, ctx)


class VisitorWithScope(Visitor):
    def __init__(self, scope: Optional[Scope] = None):
        super().__init__()
        self.scope: Scope = scope or Scope(None, scopes.Root())

    def accept_with_scope(self, scope: Scope, node: Optional[ast.Node]) -> Any:
        current_scope = self.scope

        self.scope = scope
        result = self.accept(node)
        self.scope = current_scope

        return result

    def accept_with_child_scope(self, node: Optional[ast.Node]) -> Any:
        return self.accept_with_scope(self.scope.new_child_scope(), node)
