import dataclasses
import typing

from colc.common import fatal_problem
from colc.frontend import ast, Visitor, Type


@dataclasses.dataclass
class Value:
    index: int
    identifier: ast.Identifier
    type: Type
    data: typing.Any


class Scope:
    def __init__(self, parent: typing.Optional['Scope'] = None):
        self._parent = parent
        self._values: list[Value] = []

        if parent is None:
            self._offset = 0
        else:
            self._offset = parent._offset + len(parent._values)

    def declare(self, identifier: ast.Identifier, type: Type, data: typing.Any = None) -> Value:
        value = next(filter(lambda it: it.identifier.name == identifier.name, self._values), None)

        if value is not None:
            fatal_problem('identifier is already defined', identifier)

        value = Value(self._offset + len(self._values), identifier, type, data)
        self._values.append(value)

        return value

    def lookup(self, identifier: ast.Identifier) -> Value:
        value = next(filter(lambda it: it.identifier.name == identifier.name, self._values), None)

        if value is not None:
            return value
        if self._parent is not None:
            return self._parent.lookup(identifier)

        fatal_problem('undefined identifier', identifier)

    def new_child_scope(self) -> 'Scope':
        return Scope(self._parent)

    @staticmethod
    def from_call(call: ast.Call, parameters: list[ast.Parameter], arguments: list[int | str]) -> 'Scope':
        if len(arguments) < len(parameters):
            fatal_problem('not enough arguments', call.identifier)
        if len(arguments) > len(parameters):
            fatal_problem('too many arguments', call.identifier)

        # TODO: add type checking

        scope = Scope()
        for param, arg in zip(parameters, arguments):
            scope.declare(param.identifier, param.type, arg)

        return scope


class VisitorWithScope(Visitor):
    def __init__(self):
        super().__init__()
        self.scope = Scope()

    def accept_with_scope(self, scope: Scope, node: typing.Optional[ast.Node]) -> typing.Any:
        current_scope = self.scope

        self.scope = scope
        result = self.accept(node)
        self.scope = current_scope

        return result
