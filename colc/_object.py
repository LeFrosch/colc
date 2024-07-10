from .__about__ import __version__

from colc.backend import LExpression, Instruction, Context


class Object:
    version: str

    # main constraint
    constraint: LExpression

    # shared pool of constant definitions
    const_pool: list[str | int]

    # map from mapping name to bytecode instructions
    mappings: dict[str, list[Instruction]]

    def __init__(self, ctx: Context, constraint: LExpression, mappings: dict[str, list[Instruction]]):
        self.version = __version__
        self.constraint = constraint
        self.mappings = mappings
        self.const_pool = ctx.get_const_pool()
