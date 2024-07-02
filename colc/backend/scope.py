from colc import problems
from colc.frontend import Parameter, Call


class Scope:
    def __init__(self):
        self._declarations = {}

    def declare(self, key: str, value):
        self._declarations[key] = value

    def lookup(self, key: str):
        return self._declarations[key]

    @staticmethod
    def from_call(call: Call, parameters: list[Parameter], arguments: list) -> 'Scope':
        if len(arguments) < len(parameters):
            problems.fatal('not enough arguments', at_token=call.identifier)
        if len(arguments) > len(parameters):
            problems.fatal('too many arguments', at_token=call.identifier)

        # TODO: add type checking

        scope = Scope()
        for (param, arg) in zip(parameters, arguments):
            scope.declare(param.identifier, arg)

        return scope
