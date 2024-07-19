import dataclasses
import enum
from typing import Optional

from colc.frontend import Operator


class Opcode(enum.IntEnum):
    # basic instructions
    CONST = 0x00
    STORE = 0x01
    LOAD = 0x02

    # node interaction
    ATTR = 0x03
    KIND = 0x04

    # operators
    ADD = 0x10
    SUB = 0x11
    MUL = 0x12
    DIV = 0x13
    DIV_FLOOR = 0x14
    AND = 0x15
    OR = 0x16
    NEG = 0x17
    NOT = 0x18
    EQL = 0x19
    NEQ = 0x1A
    LES = 0x1B
    LEQ = 0x1C
    GRE = 0x1D
    GEQ = 0x1E
    MUT = 0x1F
    POW = 0x20

    # const values
    TRUE = 0x30
    FALSE = 0x31
    INT = 0x32

    # control flow
    JMP_F = 0x40
    JMP_FF = 0x41
    JMP_B = 0x42

    # iterators
    NEXT = 0x50
    HAS_NEXT = 0x51
    RANGE = 0x52
    RESET = 0x5F

    def new(self, argument: int = 0, debug: Optional[str] = None) -> 'Instruction':
        assert argument >= 0
        assert argument <= 255

        return Instruction(self, argument, debug)

    @staticmethod
    def from_operator_unary(op: Operator) -> 'Opcode':
        return op.switch(
            {
                Operator.SUB: Opcode.NEG,
                Operator.NOT: Opcode.NOT,
            }
        )

    @staticmethod
    def from_operator_binary(op: Operator) -> 'Opcode':
        return op.switch(
            {
                Operator.ADD: Opcode.ADD,
                Operator.SUB: Opcode.SUB,
                Operator.MUL: Opcode.MUL,
                Operator.DIV: Opcode.DIV,
                Operator.AND: Opcode.AND,
                Operator.OR: Opcode.OR,
                Operator.EQL: Opcode.EQL,
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
