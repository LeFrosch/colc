import dataclasses
import enum


class Opcode(enum.IntEnum):
    I_CONST = 0
    I_STORE = 1
    LOAD = 2
    I_ADD = 3
    I_SUB = 4
    I_MUL = 5
    I_DIV = 6
    I_NEG = 7
    S_CONCAT = 8

    def new(self, argument: int = 0) -> 'Instruction':
        assert argument >= 0
        assert argument <= 255

        return Instruction(self, argument)


@dataclasses.dataclass
class Instruction:
    opcode: Opcode
    argument: int

    def __getstate__(self):
        return self.opcode << 8 | self.argument

    def __setstate__(self, state):
        self.opcode = Opcode(state >> 8)
        self.argument = state & 0xFF
