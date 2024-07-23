from colc.frontend import Operator

from ._opcode import Opcode


class Label:
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f'Label({self.name})'


class Instruction:
    def __init__(self, opcode: Opcode, argument: int | Label = 0):
        self.opcode = opcode
        self.argument = argument

    def __repr__(self):
        return f'{self.opcode.name}({self.argument})'

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
                Operator.NEQ: Opcode.NEQ,
                Operator.LES: Opcode.LES,
                Operator.LEQ: Opcode.LEQ,
                Operator.GRE: Opcode.GRE,
                Operator.GEQ: Opcode.GEQ,
                Operator.MUT: Opcode.MUT,
                Operator.POW: Opcode.POW,
                Operator.CONCAT: Opcode.CONCAT,
                Operator.PREPEND: Opcode.PREPEND,
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

    def build(self) -> bytes:
        builder = bytearray()

        for i, instr in enumerate(self.instructions):
            builder.append(instr.opcode)

            if not instr.opcode.is_jmp:
                builder.append(instr.argument_value)
            else:
                label = instr.argument_label
                index = self.labels.get(label)
                assert index is not None

                builder.append(abs(i - index))

        return builder
