class Pool:
    def __init__(self):
        self.__elements = []

    def intern(self, value) -> int:
        if value in self.__elements:
            return self.__elements.index(value)
        else:
            self.__elements.append(value)
            return len(self.__elements) - 1

    def resolve(self, index: int):
        return self.__elements[index]
