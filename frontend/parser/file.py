import dataclasses

from frontend.ast import ASTNode, TypeConstraint, MainConstraint


@dataclasses.dataclass
class File:
    definitions: list[ASTNode]

    def type_constraint(self, identifier: str) -> TypeConstraint:
        constraints = [it for it in self.definitions if isinstance(it, TypeConstraint) and it.identifier == identifier]

        # TODO: ensure only one constraint

        return constraints[0]

    def main_constraint(self) -> MainConstraint:
        constraints = [it for it in self.definitions if isinstance(it, MainConstraint)]

        # TODO: ensure only one constraint

        return constraints[0]
