import enum


class Opcode(enum.IntEnum):
    # basic instructions
    CONST = 0x00
    STORE = 0x01
    LOAD = 0x02
    KIND = 0x03

    # node interaction
    ATTR = 0x04
    KIND_OF = 0x05
    WHERE = 0x06

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
    FLOAT = 0x33
    NONE = 0x34

    # control flow
    JMP_F = 0x40
    JMP_FF = 0x41
    JMP_B = 0x42

    # iterators
    NEXT = 0x50
    HAS_NEXT = 0x51
    RANGE = 0x52
    RESET = 0x5F

    @property
    def is_jmp(self) -> bool:
        return 0x40 <= self.value < 0x50
