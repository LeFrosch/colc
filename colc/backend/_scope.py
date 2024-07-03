from colc import common
from colc.frontend import ast


class Scope:
    def __init__(self):
        self._declarations = {}

    def declare(self, identifier: ast.Identifier, value):
        self._declarations[identifier.name] = value

    def lookup(self, identifier: ast.Identifier):
        result = self._declarations.get(identifier.name, None)

        if result is None:
            common.fatal_problem('undeclared identifier', identifier)

        return result

    @staticmethod
    def from_call(call: ast.Call, parameters: list[ast.Parameter], arguments: list) -> 'Scope':
        if len(arguments) < len(parameters):
            common.fatal_problem('not enough arguments', call.identifier)
        if len(arguments) > len(parameters):
            common.fatal_problem('too many arguments', call.identifier)

        # TODO: add type checking

        scope = Scope()
        for param, arg in zip(parameters, arguments):
            scope.declare(param.identifier, arg)

        return scope
