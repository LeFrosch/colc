from .__about__ import __version__

from colc.backend import LExpression, Instruction, Context


class Object:
    version: str
    constraint: LExpression
    const_pool: list[str | int]
    mappings: dict[str, list[Instruction]]

    def __init__(self, ctx: Context, constraint: LExpression, mappings: dict[str, list[Instruction]]):
        self.version = __version__
        self.constraint = constraint
        self.mappings = mappings
        self.const_pool = ctx.const_pool
