import dataclasses
import enum

from colc.frontend import Operator


class Opcode(enum.IntEnum):
    CONST = 0
    STORE = 1
    LOAD = 2
    ADD = 3
    SUB = 4
    MUL = 5
    DIV = 6
    NEG = 7
    ATTR = 8

    def new(self, argument: int = 0) -> 'Instruction':
        assert argument >= 0
        assert argument <= 255

        return Instruction(self, argument)

    @staticmethod
    def from_operator(op: Operator) -> 'Opcode':
        return op.switch(
            {
                Operator.ADD: Opcode.ADD,
                Operator.SUB: Opcode.SUB,
                Operator.MUL: Opcode.MUL,
                Operator.DIV: Opcode.DIV,
            }
        )


@dataclasses.dataclass
class Instruction:
    opcode: Opcode
    argument: int

    def __getstate__(self):
        return self.opcode << 8 | self.argument

    def __setstate__(self, state):
        self.opcode = Opcode(state >> 8)
        self.argument = state & 0xFF
