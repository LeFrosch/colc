import dataclasses
import enum


class Opcode(enum.IntEnum):
    I_CONST = 0
    I_STORE = 1
    I_LOAD = 2
    I_OP = 3

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
