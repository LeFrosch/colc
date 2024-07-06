from .__about__ import __version__

from colc.backend import LExpression, Instruction


class Object:
    version: str
    constraint: LExpression
    mappings: dict[str, list[Instruction]]

    def __init__(self, constraint: LExpression, mappings: dict[str, list[Instruction]]):
        self.version = __version__
        self.constraint = constraint
        self.mappings = mappings
