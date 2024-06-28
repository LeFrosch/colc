import dataclasses

from frontend.ast import ASTNode, TypeConstraint, MainConstraint


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

    def type_constraint(self, identifier: str) -> TypeConstraint:
        constraints = [it for it in self.definitions if isinstance(it, TypeConstraint) and it.identifier == identifier]

        # TODO: ensure only one constraint

        return constraints[0]

    def main_constraint(self) -> MainConstraint:
        constraints = [it for it in self.definitions if isinstance(it, MainConstraint)]

        # TODO: ensure only one constraint

        return constraints[0]

    def intern_constant(self, constant: int | str) -> int:
        return self.constants_pool.intern(constant)
