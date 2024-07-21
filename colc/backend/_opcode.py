import enum


class Opcode(enum.IntEnum):
    # basic instructions
    CONST = 0x00
    STORE = 0x01
    LOAD = 0x02
    KIND = 0x03
    STR_OF = 0x04
    DROP = 0x05
    FAIL = 0x06

    # node interaction
    ATTR = 0x10
    KIND_OF = 0x11
    WHERE = 0x12
    EXEC = 0x13

    # operators
    ADD = 0x20
    SUB = 0x21
    MUL = 0x22
    DIV = 0x23
    DIV_FLOOR = 0x24
    AND = 0x25
    OR = 0x26
    NEG = 0x27
    NOT = 0x28
    EQL = 0x29
    NEQ = 0x2A
    LES = 0x2B
    LEQ = 0x2C
    GRE = 0x2D
    GEQ = 0x2E
    MUT = 0x2F
    POW = 0x30

    # const values
    TRUE = 0x40
    FALSE = 0x41
    INT = 0x42
    FLOAT = 0x43
    NONE = 0x44

    # control flow
    JMP_F = 0x50
    JMP_FF = 0x51
    JMP_B = 0x52

    # lists
    LIST = 0x60
    APPEND = 0x61
    REMOVE = 0x62
    LENGTH = 0x63
    RANGE = 0x64
    ITER = 0x65
    NEXT = 0x66
    HAS_NEXT = 0x67
    RESET = 0x68

    @property
    def is_jmp(self) -> bool:
        return 0x50 <= self.value < 0x60
