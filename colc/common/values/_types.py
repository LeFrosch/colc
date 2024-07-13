from ._type import Type, PrimitiveType

ANY: Type = Type(set(PrimitiveType))
ANY_LIST: Type = Type(set(PrimitiveType), list=True)
NONE: Type = Type(set())

INTEGER: Type = Type({PrimitiveType.INTEGER})
STRING: Type = Type({PrimitiveType.STRING})
BOOLEAN: Type = Type({PrimitiveType.BOOLEAN})
NODE: Type = Type({PrimitiveType.NODE})
NODE_KIND: Type = Type({PrimitiveType.NODE_KIND})

LIST_INTEGER: Type = Type({PrimitiveType.INTEGER}, list=True)
LIST_NODE: Type = Type({PrimitiveType.NODE}, list=True)
