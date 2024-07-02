import lark

from colc import problems
from colc.frontend import Node, CDefinitionType, CDefinitionMain, PDefinition, Definition


class Pool:
    def __init__(self):
        self.__elements = []

    def intern(self, value) -> int:
        if value in self.__elements:
            return self.__elements.index(value)
        else:
            self.__elements.append(value)
            return len(self.__elements) - 1

    def resolve(self, index: int):
        return self.__elements[index]


class File:
    def __init__(self, definitions: list[Node]):
        self.definitions = definitions
        self.constants_pool = Pool()

    def _report_problems(self, identifier: lark.Token, definitions: list[Definition]):
        if len(definitions) == 0:
            problems.fatal('undefined identifier', at_token=identifier)
        if len(definitions) > 1:
            problems.fatal('already defined', at_token=definitions[1].identifier)

    def constraint_type(self, identifier: lark.Token) -> CDefinitionType:
        constraints = [it for it in self.definitions if isinstance(it, CDefinitionType) and it.identifier == identifier]
        self._report_problems(identifier, constraints)

        return constraints[0]

    def constraint_main(self) -> CDefinitionMain:
        constraints = [it for it in self.definitions if isinstance(it, CDefinitionMain)]

        if len(constraints) == 0:
            problems.fatal('main constraint is undefined')
        elif len(constraints) > 1:
            problems.fatal('already defined', at_token=constraints[1].identifier)

        return constraints[0]

    def predicate(self, identifier: lark.Token) -> PDefinition:
        constraints = [it for it in self.definitions if isinstance(it, PDefinition) and it.identifier == identifier]
        self._report_problems(identifier, constraints)

        return constraints[0]

    def intern_constant(self, constant: int | str) -> int:
        return self.constants_pool.intern(constant)
