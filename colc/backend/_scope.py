import dataclasses
import abc
import itertools
from typing import Optional, Any

from colc.common import fatal_problem, internal_problem
from colc.frontend import ast, Visitor, Value, RuntimeValue, ComptimeValue, Type, Qualifier


@dataclasses.dataclass
class Definition(abc.ABC):
    name: str
    value: Value

    @property
    def is_comptime(self) -> bool:
        return self.value.is_comptime

    @property
    def is_runtime(self) -> bool:
        return self.value.is_runtime

    @property
    @abc.abstractmethod
    def is_final(self) -> bool: ...


@dataclasses.dataclass
class RuntimeDefinition(Definition):
    index: int
    value: RuntimeValue
    final: bool

    @property
    def is_final(self) -> bool:
        return self.final


@dataclasses.dataclass
class ComptimeDefinition(Definition):
    value: ComptimeValue

    @property
    def is_final(self) -> bool:
        return True


class Allocator:
    def __init__(self):
        self.index: int = 0

    def alloc(self) -> int:
        self.index += 1
        return self.index - 1


class Scope:
    def __init__(self, allocator: Allocator, parent: Optional['Scope']):
        self._allocator = allocator
        self._parent = parent
        self._runtime_definitions: list[RuntimeDefinition] = []
        self._comptime_definitions: list[ComptimeDefinition] = []

    def _find_definition(self, name: str) -> Optional[Definition]:
        # check runtime values first, comptime definition might have been demoted to runtime
        definitions = itertools.chain(self._runtime_definitions, self._comptime_definitions)
        return next((it for it in definitions if it.name == name), None)

    def _define_comptime(self, name: str, value: ComptimeValue) -> Definition:
        definition = ComptimeDefinition(name, value)
        self._comptime_definitions.append(definition)
        return definition

    def _define_runtime(self, name: str, value: RuntimeValue, final: bool) -> Definition:
        runtime = RuntimeDefinition(name, value, self._allocator.alloc(), final)
        self._runtime_definitions.append(runtime)
        return runtime

    def define(self, identifier: ast.Identifier, value: Value, qualifier: Qualifier) -> Definition:
        definition = self._find_definition(identifier.name)
        if definition is not None:
            fatal_problem('identifier is already defined', identifier)

        if value.is_none:
            fatal_problem('cannot assign <none>', identifier)

        if qualifier == Qualifier.CONST:
            if isinstance(value, ComptimeValue):
                return self._define_comptime(identifier.name, value)
            else:
                fatal_problem('cannot assign runtime value', identifier)
        else:
            return self._define_runtime(identifier.name, value.as_runtime, final=qualifier == Qualifier.FINAL)

    def define_synthetic(self, name: str, type: Type) -> Definition:
        definition = self._find_definition(name)
        if definition is not None:
            internal_problem(f'synthetic identifier is already defined {name}')

        return self._define_runtime(name, RuntimeValue({type}), final=True)

    def lookup(self, identifier: ast.Identifier, expected: Optional[Type] = None) -> Definition:
        definition = self._find_definition(identifier.name)

        if definition is None and self._parent is not None:
            definition = self._parent.lookup(identifier)
        if definition is None:
            fatal_problem('undefined identifier', identifier)

        if expected is not None and not definition.value.assignable_to(expected):
            fatal_problem(f'expected identifier of type {expected}', identifier)

        return definition

    def assign(self, identifier: ast.Identifier, value: Value) -> RuntimeDefinition:
        definition = self.lookup(identifier)
        if not isinstance(definition, RuntimeDefinition):
            fatal_problem('cannot assign to const identifier', identifier)
        if definition.is_final:
            fatal_problem('cannot assign to final identifier', identifier)

        if not value.assignable_to(definition.value.possible_types):
            fatal_problem(f'cannot assign {value} to {definition.value} identifier', identifier)

        # there is no actual assignment, all comptime values are final
        return definition

    def new_call_scope(self) -> 'Scope':
        return Scope(self._allocator, None)

    def new_child_scope(self) -> 'Scope':
        return Scope(self._allocator, self)


class VisitorWithScope(Visitor):
    def __init__(self, scope: Optional[Scope] = None):
        super().__init__()
        self.scope = scope or Scope(Allocator(), None)

    def accept_with_scope(self, scope: Scope, node: Optional[ast.Node]) -> Any:
        current_scope = self.scope

        self.scope = scope
        result = self.accept(node)
        self.scope = current_scope

        return result

    def accept_with_child_scope(self, node: Optional[ast.Node]) -> Any:
        return self.accept_with_scope(self.scope.new_child_scope(), node)
