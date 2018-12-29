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

class LtnsKeyword(str):
    def __new__(cls, value, **kwargs):
        return super().__new__(cls, value, **kwargs)

class LtnsString(str):
    def __new__(cls, s, **kwargs):
        return super().__new__(cls, s, **kwargs)

class LtnsSymbol(str):
    def __new__(cls, name, **kwargs):
        return super().__new__(cls, name, **kwargs)

class LtnsList(list):
    def __new__(cls, elements, **kwargs):
        return super().__new__(cls, elements, **kwargs)
