from frontend.ast import ASTNode, CDefinitionType, CDefinitionMain, PDefinition


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
    def __init__(self, definitions: list[ASTNode]):
        self.definitions = definitions
        self.constants_pool = Pool()

    def constraint_type(self, identifier: str) -> CDefinitionType:
        constraints = [it for it in self.definitions if isinstance(it, CDefinitionType) and it.identifier == identifier]

        # TODO: ensure only one constraint

        return constraints[0]

    def constraint_main(self) -> CDefinitionMain:
        constraints = [it for it in self.definitions if isinstance(it, CDefinitionMain)]

        # TODO: ensure only one constraint

        return constraints[0]

    def predicate(self, identifier: str) -> PDefinition:
        constraints = [it for it in self.definitions if isinstance(it, PDefinition) and it.identifier == identifier]

        # TODO: ensure only one constraint

        return constraints[0]

    def intern_constant(self, constant: int | str) -> int:
        return self.constants_pool.intern(constant)
