import dataclasses
import enum
from typing import Optional

from colc.frontend import Operator


class Opcode(enum.IntEnum):
    # basic instructions
    CONST = 0x00
    STORE = 0x01
    LOAD = 0x02
    ATTR = 0x03

    # operators
    ADD = 0x10
    SUB = 0x11
    MUL = 0x12
    DIV = 0x13
    AND = 0x14
    OR = 0x15
    NEG = 0x16
    NOT = 0x17
    EQL = 0x18
    NEQ = 0x19
    LES = 0x1A
    LEQ = 0x1B
    GRE = 0x1C
    GEQ = 0x1D
    MUT = 0x1E
    POW = 0x1F

    # const values
    TRUE = 0x20
    FALSE = 0x21
    INT = 0x22

    def new(self, argument: int = 0, debug: Optional[str] = None) -> 'Instruction':
        assert argument >= 0
        assert argument <= 255

        return Instruction(self, argument, debug)

    @staticmethod
    def from_operator(op: Operator) -> 'Opcode':
        return op.switch(
            {
                Operator.ADD: Opcode.ADD,
                Operator.SUB: Opcode.SUB,
                Operator.MUL: Opcode.MUL,
                Operator.DIV: Opcode.DIV,
                Operator.AND: Opcode.AND,
                Operator.OR: Opcode.OR,
                Operator.EQL: Opcode.EQL,
                Operator.NEQ: Opcode.NEQ,
                Operator.LES: Opcode.LES,
                Operator.LEQ: Opcode.LEQ,
                Operator.GRE: Opcode.GRE,
                Operator.GEQ: Opcode.GEQ,
                Operator.MUT: Opcode.MUT,
                Operator.POW: Opcode.POW,
            }
        )


@dataclasses.dataclass
class Instruction:
    opcode: Opcode
    argument: int
    debug: Optional[str]

    def __getstate__(self):
        return self.opcode << 8 | self.argument

    def __setstate__(self, state):
        self.opcode = Opcode(state >> 8)
        self.argument = state & 0xFF
        self.debug = None
