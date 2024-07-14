from ._instruction import Instruction, Opcode


class JmpAnchor:
    def __init__(self, instructions: list[Instruction], opcode: Opcode):
        self._instructions = instructions
        self._instruction = opcode.new(0)

        instructions.append(self._instruction)
        self._address = len(instructions)

    def set_address(self):
        offset = len(self._instructions) - self._address

        if offset == 0:
            # relative jumps with length 0 are useless
            self._instructions.pop()
        else:
            assert offset < 265

            self._instruction.argument = offset
            self._instruction.debug = str(len(self._instructions))
