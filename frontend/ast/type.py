import enum
import lark


class Type(enum.Enum):
    STRING = 0
    INTEGER = 1

    @staticmethod
    def from_token(token: lark.Token) -> 'Type':
        if token == "str":
            return Type.STRING
        elif token == "int":
            return Type.INTEGER
        else:
            raise "Unknown type"
