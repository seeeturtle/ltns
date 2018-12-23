from functools import reduce


class LtnsElement:
    def __init__(self, name, **kwargs):
        self.name = name
        self.attributes = kwargs.pop('attributes', {})
        self.childs = kwargs.pop('childs', [])

class LtnsInteger(int):
    def __new__(cls, n, **kwargs):
        return super().__new__(cls, n, **kwargs)

class LtnsFloat(float):
    def __new__(cls, n, **kwargs):
        return super().__new__(cls, n, **kwargs)

class LtnsComplex(complex):
    def __new__(cls, n, **kwargs):
        return super().__new__(cls, n, **kwargs)

class LtnsKeyword:
    def __init__(self, name, **kwargs):
        self.value = name

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return reduce(
            lambda x, y: 1/2*(x+y)*(x+y+1)+y,
            (ord(c) for c in self.value))

class LtnsString(str):
    def __new__(cls, s, **kwargs):
        return super().__new__(cls, s, **kwargs)

class LtnsSymbol:
    def __init__(self, name, **kwargs):
        self.name = name

class LtnsList(list):
    def __new__(cls, elements, **kwargs):
        return super().__new__(cls, elements, **kwargs)
