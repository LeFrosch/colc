from colc.frontend import Operator

from ._opcode import Opcode


class Label:
    def __init__(self, name: str):
        self.name = name


class Instruction:
    def __init__(self, opcode: Opcode, argument: int | Label = 0):
        self.opcode = opcode
        self.argument = argument

    @property
    def argument_label(self) -> Label:
        assert isinstance(self.argument, Label)
        return self.argument

    @property
    def argument_value(self) -> int:
        assert isinstance(self.argument, int)
        return self.argument

    @staticmethod
    def new_store(index: int):
        return Instruction(Opcode.STORE, argument=index)

    @staticmethod
    def new_load(index: int):
        return Instruction(Opcode.LOAD, argument=index)

    @staticmethod
    def new_jmp(opcode: Opcode, label: Label):
        return Instruction(opcode, argument=label)

    @staticmethod
    def new_unary_operator(operator: Operator):
        opcode = operator.switch(
            {
                Operator.SUB: Opcode.NEG,
                Operator.NOT: Opcode.NOT,
            }
        )

        return Instruction(opcode)

    @staticmethod
    def new_binary_operator(operator: Operator):
        opcode = operator.switch(
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

        return Instruction(opcode)


class InstructionBuffer:
    def __init__(self):
        self.instructions: list[Instruction] = []
        self.labels: dict[Label, int] = {}

    def add(self, instruction: Instruction):
        self.instructions.append(instruction)

    def add_label(self, label: Label):
        self.labels[label] = len(self.instructions)
