from colc import problems
from colc.frontend import Parameter, Call, Identifier


class Scope:
    def __init__(self):
        self._declarations = {}

    def declare(self, identifier: Identifier, value):
        self._declarations[identifier.name] = value

    def lookup(self, identifier: Identifier):
        result = self._declarations.get(identifier.name, None)

        if result is None:
            problems.fatal('undeclared identifier', identifier)

        return result

    @staticmethod
    def from_call(call: Call, parameters: list[Parameter], arguments: list) -> 'Scope':
        if len(arguments) < len(parameters):
            problems.fatal('not enough arguments', call.identifier)
        if len(arguments) > len(parameters):
            problems.fatal('too many arguments', call.identifier)

        # TODO: add type checking

        scope = Scope()
        for param, arg in zip(parameters, arguments):
            scope.declare(param.identifier, arg)

        return scope
