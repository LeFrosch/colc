import enum
import lark


class ASTEnum(enum.Enum):
    def switch[T](self, cases: dict['ASTEnum', T]) -> T:
        return cases[self]

    @classmethod
    def from_token(cls, token: lark.Token):
        for element in cls:
            if element.value == token:
                return element

        raise f'Unknown element in {cls.__name__}: {token}'


class Comparison(ASTEnum):
    EQUAL = '=='
    NOT_EQUAL = '!='
    LESS = '<'
    LESS_EQUAL = '<='
    GREATER = '>'
    GREATER_EQUAL = '>='
    MULTIPLE = '*='
    POWER = '**='


class Operator(ASTEnum):
    PLUS = '+'
    MINUS = '-'
    MULTIPLICATION = '*'
    DIVISION = '/'


class Quantifier(ASTEnum):
    ALL = 'all:'
    ANY = 'any:'
    ONE = 'one:'


class Aggregator(ASTEnum):
    MIN = 'min'
    MAX = 'max'
    SUM = 'sum'
    AVG = 'avg'
