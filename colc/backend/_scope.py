import dataclasses
import abc
import itertools
from typing import Optional, Any

from colc.common import fatal_problem, internal_problem
from colc.frontend import ast, Visitor, Value, RuntimeValue, ComptimeValue, DefaultValue, Type

from ._operator import type_check


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


@dataclasses.dataclass
class RuntimeDefinition(Definition):
    index: int
    value: RuntimeValue


@dataclasses.dataclass
class ComptimeDefinition(Definition):
    value: ComptimeValue


class Scope:
    def __init__(self, parent: Optional['Scope'] = None):
        self._parent = parent
        self._runtime_definitions: list[RuntimeDefinition] = []
        self._comptime_definitions: list[ComptimeDefinition] = []

        if parent is None:
            self._offset = 0
        else:
            self._offset = parent._offset + len(parent._runtime_definitions)

    def _find_definition(self, name: str) -> Optional[Definition]:
        definitions = itertools.chain(self._runtime_definitions, self._comptime_definitions)
        return next((it for it in definitions if it.name == name), None)

    def _define(self, name: str, value: Value) -> Definition:
        if isinstance(value, RuntimeValue):
            runtime = RuntimeDefinition(name, value, self._offset + len(self._runtime_definitions))
            self._runtime_definitions.append(runtime)
            return runtime
        elif isinstance(value, ComptimeValue):
            comptime = ComptimeDefinition(name, value)
            self._comptime_definitions.append(comptime)
            return comptime
        else:
            internal_problem(f'unknown value {value}')

    def define(self, identifier: ast.Identifier, value: Value = DefaultValue) -> Definition:
        definition = self._find_definition(identifier.name)

        if definition is not None:
            fatal_problem('identifier is already defined', identifier)

        return self._define(identifier.name, value)

    def define_synthetic(self, name: str, value: Value) -> Definition:
        definition = self._find_definition(name)

        if definition is not None:
            internal_problem(f'synthetic identifier is already defined {name}')

        return self._define(name, value)

    def lookup(self, identifier: ast.Identifier) -> Definition:
        definition = self._find_definition(identifier.name)

        if definition is not None:
            return definition
        if self._parent is not None:
            return self._parent.lookup(identifier)

        fatal_problem('undefined identifier', identifier)

    def lookup_runtime(self, identifier: ast.Identifier, expected_type: Optional[Type] = None) -> RuntimeDefinition:
        definition = self.lookup(identifier)

        # do type check first, because this error is easier to understand
        if not type_check(definition.value, expected_type):
            fatal_problem(f'expected identifier of type {expected_type}', identifier)

        # not sure if this actually is an internal problem or if there are cases where this is just fatal
        if not isinstance(definition, RuntimeDefinition):
            internal_problem(f'expected runtime definition {definition.name}')

        return definition

    def new_child_scope(self) -> 'Scope':
        return Scope(self._parent)


class VisitorWithScope(Visitor):
    def __init__(self, scope: Optional[Scope] = None):
        super().__init__()
        self.scope = scope or Scope()

    def accept_with_scope(self, scope: Scope, node: Optional[ast.Node]) -> Any:
        current_scope = self.scope

        self.scope = scope
        result = self.accept(node)
        self.scope = current_scope

        return result
